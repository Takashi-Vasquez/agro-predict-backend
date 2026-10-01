from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional


@dataclass
class ModelVersion:
    id: int
    model_name: str
    version: str
    status: str
    trained_at: datetime
    git_commit: Optional[str] = None
    data_version: Optional[str] = None
    data_from: Optional[date] = None
    data_to: Optional[date] = None
    features: Optional[list] = None
    candidates_evaluated: Optional[dict[str, Any]] = None
    metrics: Optional[dict[str, float]] = None
    baseline_compared: Optional[str] = None
    base_version_id: Optional[int] = None
    artifact_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None