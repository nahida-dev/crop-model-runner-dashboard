import csv
import io
import os
import time
import random
import typing as t
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_KEY = os.getenv("USDA_API_KEY", "YOUR_API_KEY_HERE")
STATES = ["IA","IL","IN","OH","KS","MI"]
YEAR_GE = 2010
YEAR_LE = 2020
BASE_URL = "https://quickstats.nass.usda.gov/api/api_GET/"

OUT_DIR = Path("backend/data")
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR = OUT_DIR / "tmp_qs"
TMP_DIR.mkdir(parents=True, exist_ok=True)

# -------- HTTP session with retries (429/5xx) ----------
def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=10,
        read=10,
        connect=10,
        backoff_factor=2.0,  # exponential backoff
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    s.headers.update({
        "User-Agent": "model-runner/1.0 (FastAPI demo) contact: you@example.com"
    })
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s

def norm_value_to_float(value: t.Any) -> t.Optional[float]:
    if pd.isna(value):
        return None
    s = str(value).strip()
    if s in {"(D)", "(Z)", "(NA)"}:
        return None
    s = s.replace(",", "")
    try:
        return float(s)
    except:
        return None

def to_region_label(state_alpha: str, asd_desc: str) -> str:
    parts = asd_desc.strip().lower().split()
    titled = "".join(p.capitalize() for p in parts)  # "north central" -> "NorthCentral"
    return f"{state_alpha}-{titled}"

def qs_get_csv(session: requests.Session, base_params: dict, variant_params_list: list[dict]) -> pd.DataFrame:
    """
    Try a list of param variants for the same query intent.
    If a variant 400s or returns '(en) Please come back later', retry with backoff and then try the next variant.
    Returns the first non-empty DataFrame.
    """
    for variant in variant_params_list:
        # Merge defaults + variant
        params = {
            "key": API_KEY,
            "format": "CSV",
            "year__GE": YEAR_GE,
            "year__LE": YEAR_LE,
            **base_params,
            **variant,
        }
        last_text = None
        for attempt in range(6):
            resp = session.get(BASE_URL, params=params, timeout=60)
            text = resp.text.strip()
            last_text = text
            # throttle/overload
            if "(en) Please come back later" in text or resp.status_code in (429, 500, 502, 503, 504):
                time.sleep((2 ** attempt) + random.uniform(0, 2))
                continue
            if resp.status_code == 400:
                # USDA returns generic 400 text, just try next variant
                break
            resp.raise_for_status()
            try:
                df = pd.read_csv(io.StringIO(text))
                if not df.empty:
                    return df
            except Exception:
                # sometimes HTML on overload; retry
                time.sleep((2 ** attempt) + random.uniform(0, 2))
                continue
        # next variant
    raise RuntimeError("QuickStats returned 400/empty for all variants of this query. Last server text:\n" + (last_text or "n/a"))

def fetch_state_yield(state: str, session: requests.Session) -> pd.DataFrame:
    """
    Corn Yield (BU/ACRE), Agricultural District. Tries multiple short_desc variants
    known to exist in QuickStats for some states/years.
    """
    base = {
        "state_alpha": state,
        "agg_level_desc": "AGRICULTURAL DISTRICT",
        # optional scoping that usually helps:
        "source_desc": "SURVEY",
        "sector_desc": "CROPS",
        "group_desc": "FIELD CROPS",
        "commodity_desc": "CORN",
    }

    variants = [
        # Most common
        {"short_desc": "CORN, GRAIN - YIELD, MEASURED IN BU / ACRE"},
        # Sometimes appears without ", GRAIN"
        {"short_desc": "CORN - YIELD, MEASURED IN BU / ACRE"},
        # Fallback via statisticcat+unit (no short_desc)
        {"statisticcat_desc": "YIELD", "unit_desc": "BU / ACRE"},
        # Relax unit_desc (you can filter unit later in code)
        {"statisticcat_desc": "YIELD"},
    ]

    df = qs_get_csv(session, base, variants)
    # Normalize
    if "Value" not in df.columns or "asd_desc" not in df.columns:
        raise RuntimeError("Unexpected QuickStats schema for yield; got columns: " + ", ".join(df.columns))

    df["yield_bu_acre"] = df["Value"].apply(norm_value_to_float)
    df = df.dropna(subset=["yield_bu_acre"])
    df["region"] = df.apply(lambda r: to_region_label(r["state_alpha"], r["asd_desc"]), axis=1)
    df = df[["region", "year", "yield_bu_acre"]].copy()
    df = df.groupby(["region", "year"], as_index=False)["yield_bu_acre"].mean()

    # Sanity check: If no rows, try STATE level once to confirm data exists
    if df.empty:
        base_state = base.copy()
        base_state["agg_level_desc"] = "STATE"
        df_state = qs_get_csv(session, base_state, [
            {"short_desc": "CORN, GRAIN - YIELD, MEASURED IN BU / ACRE"},
            {"short_desc": "CORN - YIELD, MEASURED IN BU / ACRE"},
            {"statisticcat_desc": "YIELD", "unit_desc": "BU / ACRE"},
            {"statisticcat_desc": "YIELD"},
        ])
        if df_state.empty:
            raise RuntimeError(f"No YIELD rows for {state} even at STATE level—try a different year range or time of day.")
    return df

def fetch_state_area(state: str, session: requests.Session) -> pd.DataFrame:
    """
    Corn Area Harvested (ACRES), Agricultural District. Multiple variants + fallback.
    """
    base = {
        "state_alpha": state,
        "agg_level_desc": "AGRICULTURAL DISTRICT",
        "source_desc": "SURVEY",
        "sector_desc": "CROPS",
        "group_desc": "FIELD CROPS",
        "commodity_desc": "CORN",
    }

    variants = [
        {"short_desc": "CORN, GRAIN - ACRES HARVESTED"},
        {"short_desc": "CORN - ACRES HARVESTED"},
        {"statisticcat_desc": "AREA HARVESTED", "unit_desc": "ACRES"},
        {"statisticcat_desc": "AREA HARVESTED"},
    ]

    df = qs_get_csv(session, base, variants)
    if "Value" not in df.columns or "asd_desc" not in df.columns:
        raise RuntimeError("Unexpected QuickStats schema for area; got columns: " + ", ".join(df.columns))

    df["acres"] = df["Value"].apply(norm_value_to_float)
    df = df.dropna(subset=["acres"])
    df["region"] = df.apply(lambda r: to_region_label(r["state_alpha"], r["asd_desc"]), axis=1)
    df = df[["region", "year", "acres"]].copy()
    df = df.groupby(["region", "year"], as_index=False)["acres"].sum()

    if df.empty:
        base_state = base.copy()
        base_state["agg_level_desc"] = "STATE"
        df_state = qs_get_csv(session, base_state, [
            {"short_desc": "CORN, GRAIN - ACRES HARVESTED"},
            {"short_desc": "CORN - ACRES HARVESTED"},
            {"statisticcat_desc": "AREA HARVESTED", "unit_desc": "ACRES"},
            {"statisticcat_desc": "AREA HARVESTED"},
        ])
        if df_state.empty:
            raise RuntimeError(f"No AREA HARVESTED rows for {state} even at STATE level—try a different year range or time of day.")
    return df

def main():
    if API_KEY == "YOUR_API_KEY_HERE":
        raise SystemExit("Set USDA_API_KEY env var or edit API_KEY in this script.")

    session = make_session()

    # Collect per-state partials (persist after each state)
    yield_parts = []
    area_parts = []

    for idx, st in enumerate(STATES, start=1):
        print(f"[{idx}/{len(STATES)}] Fetching YIELD for {st} …")
        y = fetch_state_yield(st, session)
        y.to_csv(TMP_DIR / f"yield_{st}.csv", index=False)
        yield_parts.append(y)

        # polite delay with jitter between calls
        time.sleep(2 + random.uniform(0.5, 1.5))

        print(f"[{idx}/{len(STATES)}] Fetching AREA HARVESTED for {st} …")
        a = fetch_state_area(st, session)
        a.to_csv(TMP_DIR / f"area_{st}.csv", index=False)
        area_parts.append(a)

        # longer sleep after full state cycle
        time.sleep(4 + random.uniform(0.5, 2.0))

    # Merge all states
    yield_df = pd.concat(yield_parts, ignore_index=True) if yield_parts else pd.DataFrame(columns=["region","year","yield_bu_acre"])
    area_df = pd.concat(area_parts, ignore_index=True) if area_parts else pd.DataFrame(columns=["region","year","acres"])

    merged = pd.merge(yield_df, area_df, on=["region","year"], how="inner")
    out = merged[["region","year","acres","yield_bu_acre"]].rename(columns={"yield_bu_acre": "expected_yield_bu_acre"})
    out = out.sort_values(["region","year"]).reset_index(drop=True)

    out_path = OUT_DIR / "yield_data.csv"
    out.to_csv(out_path, index=False)
    print(f"✅ Wrote {len(out)} rows to {out_path}")
    print(out.head(12).to_string(index=False))

if __name__ == "__main__":
    main()
