# Pydantic I/O models (no table=True)
from sqlmodel import SQLModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

# Requests
class RunRequest(SQLModel):
    model_id: str
    region: str
    year: int    

# Responses
class RunCreatedResponse(SQLModel):
    run_id: int

class RunStatusResponse(SQLModel):
    run_id: int
    status: str
    started_at: datetime
    finished_at: Optional[datetime]

class RunResultsResponse(SQLModel):
    summaryMetrics: Dict[str, Any]
    table: List[Dict[str, Any]]

class ModelListItem(SQLModel):
    model_id: str
    name: str
    description: Optional[str] = None
