from sqlmodel import SQLModel, Field, Relationship
from typing import Dict, List, Any, Optional
from datetime import datetime

class ModelInfo(SQLModel, table=True):
    model_id: str = Field(primary_key=True)
    name: str
    description: Optional[str] = None

class Run(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    model_id: str
    user_id: str
    status: str  # e.g. "queued", "preprocessing", "computing", "succeeded", "failed"

    params_json: str  # we store region/year here as JSON text

    result_summary_json: Optional[str] = None  # JSON string of summary metrics
    result_table_json: Optional[str] = None    # JSON string of tabular rows

    created_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None

class RunResult(SQLModel, table=True):
    result_id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int
    summary_metrics: str
    result_table: str
