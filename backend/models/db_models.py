from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional

import sqlalchemy as sa
from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Column


class ModelInfo(SQLModel, table=True):
    __tablename__: ClassVar[str] = "models"
    model_config: ClassVar[ConfigDict] = ConfigDict(protected_namespaces=())

    # string PK like "crop_yield_predictor"
    model_id: str = Field(primary_key=True)
    name: str
    description: Optional[str] = None


class Run(SQLModel, table=True):
    __tablename__: ClassVar[str] = "runs"  # <<— IMPORTANT: must be "runs"
    model_config: ClassVar[ConfigDict] = ConfigDict(protected_namespaces=())

    id: Optional[int] = Field(default=None, primary_key=True)

    # If you want a hard FK, use: sa_column=Column(sa.String, sa.ForeignKey("models.model_id"), index=True)
    model_id: str = Field(index=True)

    user_id: str = Field(index=True)
    status: str = Field(index=True)  # "queued" | "preprocessing" | ...

    params_json: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(sa.JSON, nullable=False),
    )

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    finished_at: Optional[datetime] = None


class RunResult(SQLModel, table=True):
    __tablename__: ClassVar[str] = "run_results"
    model_config: ClassVar[ConfigDict] = ConfigDict(protected_namespaces=())

    # 1:1 PK == FK to runs.id (this MUST reference "runs.id" to match Run.__tablename__)
    run_id: int = Field(primary_key=True, foreign_key="runs.id")

    summary_json: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(sa.JSON, nullable=False),
    )
    table_json: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(sa.JSON, nullable=False),
    )
