from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional


@dataclass
class ModelRun:
    id: int
    model_version_id: Optional[int] = None
    trained_at: datetime = None
    git_commit: Optional[str] = None
    data_version: Optional[str] = None
    data_from: Optional[date] = None
    data_to: Optional[date] = None
    candidates_evaluated: Optional[dict[str, Any]] = None
    winner: Optional[str] = None
    improvement_vs_baseline: Optional[float] = None
    generated_version: bool = False
    reason_no_version: Optional[str] = None
    duration_seconds: Optional[int] = None