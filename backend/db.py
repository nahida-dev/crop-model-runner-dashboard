import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Session, create_engine, select
from pathlib import Path
from .models.db_models import ModelInfo, Run, RunResult

# Build an absolute path to backend/data/runs.db
BASE_DIR = Path(__file__).resolve().parent  # this is backend/
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)  # make sure the folder exists

DB_PATH = DATA_DIR / "runs.db"
DB_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(DB_URL, echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing = session.exec(select(ModelInfo)).all()
        if not existing:
            session.add_all([
                ModelInfo(
                    model_id="crop_yield_predictor",
                    name="Crop Yield Predictor",
                    description="Predicts expected yield using USDA public data sample"
                ),
                ModelInfo(
                    model_id="water_risk",
                    name="Water Risk Model",
                    description="Scores irrigation stress and drought risk using synthetic data"
                )
            ])
            session.commit()

def create_run(model_id: str, user_id: str, params: dict) -> int:
    run = Run(
        model_id=model_id,
        user_id=user_id,
        status="queued",
        params_json=json.dumps(params),  # <-- this should never be None now
    )
    with Session(engine) as session:
        session.add(run)
        session.commit()
        session.refresh(run)
        return run.id

def get_runs_for_user(user_id: str):
    """Return all runs that belong to a specific user."""
    with Session(engine) as session:
        statement = select(Run).where(Run.user_id == user_id).order_by(Run.created_at.desc())
        results = session.exec(statement).all()
        return results

def update_run_status(run_id: int, new_status: str):
    with Session(engine) as session:
        run = session.get(Run, run_id)
        if not run:
            return
        run.status = new_status

        # mark finished_at if this run is done
        if new_status in ["succeeded", "failed"]:
            run.finished_at = datetime.utcnow()

        session.add(run)
        session.commit()

def save_run_result(run_id: int, summary: Dict[str, Any], table_rows: List[Dict[str, Any]]):
    from .models import RunResult  # safe local import if needed
    try:
        with Session(engine) as session:
            # Try to find an existing result row for this run
            existing = session.exec(
                select(RunResult).where(RunResult.run_id == run_id)
            ).first()

            if existing:
                existing.summary_metrics = json.dumps(summary)
                existing.result_table = json.dumps(table_rows)
                session.add(existing)
            else:
                rr = RunResult(
                    run_id=run_id,
                    summary_metrics=json.dumps(summary),
                    result_table=json.dumps(table_rows),
                )
                session.add(rr)

            session.commit()
            print(f"✔ saved results for run {run_id} (rows={len(table_rows)})")
    except Exception as e:
        print(f"✗ save_run_result({run_id}) failed: {e!r}")
        raise
    
def get_run_result(run_id: int):
    from .models import RunResult
    with Session(engine) as session:
        return session.exec(
            select(RunResult).where(RunResult.run_id == run_id).order_by(RunResult.result_id.desc())
        ).first()

def get_run_for_user(run_id: int, user_id: str) -> Optional[Run]:
    with Session(engine) as session:
        run = session.get(Run, run_id)
        if not run:
            return None
        if run.user_id != user_id:
            return None
        return run

def get_run_status(run_id: int) -> Optional[Run]:
    with Session(engine) as session:
        return session.get(Run, run_id)

def get_run_result(run_id: int) -> Optional[RunResult]:
    with Session(engine) as session:
        stmt = select(RunResult).where(RunResult.run_id == run_id)
        rr = session.exec(stmt).first()
        return rr

def get_run_by_id(run_id: int):
    """Fetch a Run row by its ID from the database."""
    with Session(engine) as session:
        run = session.get(Run, run_id)
        return run
