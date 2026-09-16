from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Prediction:
    id: int = 0
    user_id: int = 0
    crop_id: int | None = None
    predicted_crop: str = ""
    probability: float = 0.0
    N: float = 0.0
    P: float = 0.0
    K: float = 0.0
    temperature: float = 0.0
    humidity: float = 0.0
    ph: float = 0.0
    rainfall: float = 0.0
    error_message: str | None = None
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
