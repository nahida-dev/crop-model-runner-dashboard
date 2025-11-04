from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from sqlmodel import SQLModel, Session, create_engine, select

from .models.db_models import ModelInfo, Run, RunResult

# Build an absolute path to backend/data/runs.db
BASE_DIR = Path(__file__).resolve().parent  # backend/
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "runs.db"
DB_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(DB_URL, echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)
    # Seed models if not present
    with Session(engine) as session:
        existing = session.exec(select(ModelInfo)).all()
        if not existing:
            session.add_all([
                ModelInfo(
                    model_id="crop_yield_predictor",
                    name="Crop Yield Predictor",
                    description="Predicts expected yield using USDA public data sample",
                ),
                ModelInfo(
                    model_id="water_risk",
                    name="Water Risk Model",
                    description="Scores irrigation stress and drought risk using synthetic data",
                ),
            ])
            session.commit()


def create_run(model_id: str, user_id: str, params: Dict[str, Any]) -> int:
    """
    Create a run; params persist as JSON (dict).
    """
    run = Run(
        model_id=model_id,
        user_id=user_id,
        status="queued",
        params_json=params,  # ← no json.dumps; JSON field stores dict
    )
    with Session(engine) as session:
        session.add(run)
        session.commit()
        session.refresh(run)
        if run is None:
            raise ValueError("Failed to create run")
        return run.id


def get_runs_for_user(user_id: str):
    with Session(engine) as session:
        statement = (
            select(Run)
            .where(Run.user_id == user_id)
            .order_by(Run.created_at.desc())
        )
        return session.exec(statement).all()


def update_run_status(run_id: int, new_status: str):
    with Session(engine) as session:
        run = session.get(Run, run_id)
        if not run:
            return
        run.status = new_status
        if new_status in ["succeeded", "failed"]:
            run.finished_at = datetime.utcnow()
        session.add(run)
        session.commit()


def save_run_result(
    run_id: int,
    summary: Dict[str, Any],
    table_rows: List[Dict[str, Any]],
):
    """
    Write results to RunResult (1:1). Overwrite if it already exists.
    """
    with Session(engine) as session:
        existing = session.exec(
            select(RunResult).where(RunResult.run_id == run_id)
        ).one_or_none()

        if existing:
            existing.summary_json = summary
            existing.table_json = table_rows
            session.add(existing)
        else:
            rr = RunResult(
                run_id=run_id,
                summary_json=summary,
                table_json=table_rows,
            )
            session.add(rr)

        session.commit()


def get_run_for_user(run_id: int, user_id: str) -> Optional[Run]:
    with Session(engine) as session:
        run = session.get(Run, run_id)
        if not run or run.user_id != user_id:
            return None
        return run


def get_run_status(run_id: int) -> Optional[Run]:
    with Session(engine) as session:
        return session.get(Run, run_id)


def get_run_result(run_id: int) -> Optional[RunResult]:
    with Session(engine) as session:
        stmt = select(RunResult).where(RunResult.run_id == run_id)
        return session.exec(stmt).one_or_none()


def get_run_by_id(run_id: int) -> Optional[Run]:
    with Session(engine) as session:
        return session.get(Run, run_id)
