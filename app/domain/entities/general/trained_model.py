from datetime import datetime
from dataclasses import dataclass


@dataclass
class TrainedModel:
    id: int
    user_id: int
    name: str
    algorithm: str
    version: str
    r2_score: float
    rmse: float
    mae: float
    feature_importance: dict | None
    hyperparameters: dict | None
    training_samples: int
    feature_names: dict | None
    artifact_path: str
    is_selected: bool
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
