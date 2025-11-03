import asyncio, csv, random, json, os
from pathlib import Path
from typing import Dict, Any, List, Tuple
from .db import update_run_status, save_run_result

YIELD_CSV_PATH = Path(__file__).parent / "data" / "yield_data.csv"
WATER_CSV_PATH = Path(__file__).parent / "data" / "water_risk_data.csv"

# Seconds to pause after each status change (override via env var)
STEP_DELAY = float(os.getenv("RUNNER_STEP_DELAY", "3.0"))

def _lookup_yield(region: str, year: int) -> Tuple[float, float, int]:
    matches = []
    with open(YIELD_CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["region"] == region and int(row["year"]) == year:
                acres = float(row["acres"])
                yld = float(row["expected_yield_bu_acre"])
                matches.append((acres, yld))
    if not matches:
        return (0.0, 0.0, 0)
    total_acres = sum(a for a, _ in matches)
    avg_yield = sum(y for _, y in matches) / len(matches)
    total_bu = sum(a * y for a, y in matches)
    return (avg_yield, total_bu, int(total_acres))

def _compute_water_risk(region: str, year: int) -> Tuple[float, float, float, int]:
    """
    Reads backend/data/water_risk_data.csv
    Filters by region & year
    Returns (avg_drought_index, avg_irrigation_cost, avg_risk_score, num_records)
    """
    
    matches = []
    with open(WATER_CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # match region & year
            if row.get("region") == region and int(row.get("year", 0)) == year:
                drought = float(row.get("drought_index", 0))
                irrigation_cost = float(row.get("irrigation_cost_usd_per_acre", 0))
                risk_score = 0.5 * drought + 0.5 * (irrigation_cost / 100.0)
                matches.append((drought, irrigation_cost, risk_score))
    if not matches:
        # if nothing found, return zeros
        return (0.0, 0.0, 0.0, 0)
    total_drought = sum(d for d, _, _ in matches)
    total_irrigation_cost = sum(c for _, c, _ in matches)
    total_risk = sum(r for _, _, r in matches)
    n = len(matches)

    avg_drought = total_drought / n
    avg_irrigation_cost = total_irrigation_cost / n
    avg_risk = total_risk / n
    
    return (round(avg_drought, 3), round(avg_irrigation_cost, 2), round(avg_risk, 3), n)



async def execute_model_async(run_id: int, model_id: str, params: Dict[str, Any]):
    update_run_status(run_id, "running")
    await asyncio.sleep(STEP_DELAY)

    # show "computing" while doing the work
    update_run_status(run_id, "computing")
    await asyncio.sleep(STEP_DELAY)
    
    region = params.get("region")
    year = int(params.get("year", 0))
    if model_id == "crop_yield_predictor":
        avg_yield, total_bu, total_acres = _lookup_yield(region, year)
        summary = {
            "expected_yield_bu_acre": round(avg_yield, 2),
            "total_production_bu": round(total_bu, 2),
            "total_acres": total_acres,
            "region": region,
            "year": year,
        }
        table_rows = [
            {
                "region": region,
                "year": year,
                "avg_yield_bu_acre": round(avg_yield, 2),
                "total_acres": total_acres,
                "total_bu": round(total_bu, 2),
            }
        ]
    elif model_id == "water_risk":
        avg_drought, avg_irrigation_cost, avg_risk, count = _compute_water_risk(region, year)
        summary = {
            "region": region,
            "year": year,
            "avg_drought_index": avg_drought,
            "avg_irrigation_cost_usd_per_acre": avg_irrigation_cost,
            "avg_water_risk_score": avg_risk,
            "records_used": count,
        }
        table_rows = [
            {
                "region": region,
                "year": year,
                "drought_index": avg_drought,
                "irrigation_cost_usd_per_acre": avg_irrigation_cost,
                "water_risk_score": avg_risk,
                "records_used": count,
            }
        ]
    else:
        summary = {"error": "unknown model"}
        table_rows = []

    # show "postprocessing" before saving
    update_run_status(run_id, "postprocessing")
    await asyncio.sleep(STEP_DELAY)

    # save and finish
    save_run_result(run_id, summary, table_rows)
    update_run_status(run_id, "succeeded")
