from sqlmodel import SQLModel, Field
from typing import Dict, List, Any, Optional, ClassVar
from datetime import datetime
from pydantic import ConfigDict

# Requests
class RunRequest(SQLModel):
    # Make model_config a class var and use a ConfigDict (Pydantic v2)
    model_config: ClassVar[ConfigDict] = ConfigDict(protected_namespaces=())
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
    model_config: ClassVar[ConfigDict] = ConfigDict(protected_namespaces=())
    model_id: str
    name: str
    description: Optional[str] = None
