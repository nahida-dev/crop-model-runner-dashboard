import json
import asyncio
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlmodel import Session, select
from .auth import get_current_user
from .db import (
    init_db,
    create_run,
    get_run_for_user,
    get_runs_for_user,
    get_run_result,
    update_run_status,
    get_run_by_id,
)

# Tables (ORM)
from .models.db_models import ModelInfo, Run, RunResult

# Schemas (API I/O)
from .models.schemas import (    
    RunRequest, RunCreatedResponse, RunStatusResponse, RunResultsResponse, ModelListItem,  # Schemas
)
    
from .db import engine
from .runner import execute_model_async
from pathlib import Path

# import the sync runner
#from .runner import execute_model

app = FastAPI(
    title="Model Runner API",
    description="Internal dashboard backend for running and tracking analytical models.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

@app.get("/api/regions")
def get_regions(current_user: str = Depends(get_current_user)):
    """
    Return a list of distinct regions from the yield dataset.
    This powers the frontend dropdown so users don't have to guess region names.
    """
    try:
        # Build an absolute path to backend/data/yield_data.csv
        data_path = Path(__file__).resolve().parent / "data" / "yield_data.csv"
        print("Reading region list from:", data_path)

        if not data_path.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Dataset not found at {data_path}"
            )

        df = pd.read_csv(data_path)
        print("CSV columns:", list(df.columns))

        # adjust this column name if needed
        if "region" not in df.columns:
            raise HTTPException(
                status_code=500,
                detail=f"'region' column not found in CSV. Columns are: {list(df.columns)}"
            )

        regions = sorted(df["region"].unique().tolist())
        return {"regions": regions}

    except HTTPException:
        # re-raise on purpose so FastAPI uses your message
        raise
    except Exception as e:
        print("Error in /api/regions:", repr(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load regions: {e}"
        )
@app.get("/api/models", response_model=List[ModelListItem])
def list_models(current_user: str = Depends(get_current_user)):
    with Session(engine) as session:
        rows = session.exec(select(ModelInfo)).all()
        return [
            ModelListItem(
                model_id=r.model_id,
                name=r.name,
                description=r.description
            )
            for r in rows
        ]

@app.post("/api/runs", response_model=RunCreatedResponse)
async def submit_run(
    req: RunRequest,
    current_user: str = Depends(get_current_user)
):
    params = {
        "region": req.region,
        "year": req.year,        
    }
    run_id = create_run(
        model_id=req.model_id,
        user_id=current_user,
        params=params,
    )
    asyncio.create_task(
        execute_model_async(run_id, req.model_id, params)
    )
    return RunCreatedResponse(run_id=run_id)


@app.get("/api/runs")
def list_runs(current_user: str = Depends(get_current_user)):
    runs = get_runs_for_user(current_user)
    response = []
    for r in runs:
        response.append({
            "id": r.id,
            "model_id": r.model_id,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
        })
    return response    


@app.get("/api/runs/{run_id}/status")
def get_status(run_id: int, current_user: str = Depends(get_current_user)):
    run = get_run_by_id(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.user_id != current_user:
        raise HTTPException(status_code=403, detail="Forbidden for this user")

    return {
        "run_id": run.id,
        "model_id": run.model_id,
        "status": run.status,
        "started_at": run.created_at.isoformat() if run.created_at else None,
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
    }

@app.get("/api/runs/{run_id}/results")
def get_results(run_id: int, current_user: str = Depends(get_current_user)):
    run = get_run_by_id(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.user_id != current_user:
        raise HTTPException(status_code=403, detail="Forbidden for this user")

    rr = get_run_result(run_id)
    if rr is None:
        # Results not persisted yet; return empty shape the UI can handle
        return {"summaryMetrics": {}, "table": []}

    # JSON fields come back as dict/list already
    return {"summaryMetrics": rr.summary_json, "table": rr.table_json}
