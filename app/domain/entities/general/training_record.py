from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class TrainingRecord:
    id: int = 0
    user_id: int = 0
    crop_id: int | None = None
    campaign: str | None = None
    location: str | None = None

    nitrogen: float = 0.0
    phosphorus: float = 0.0
    potassium: float = 0.0
    temperature: float = 0.0
    humidity: float = 0.0
    ph_soil: float = 0.0
    rainfall: float = 0.0

    irrigation_type: str | None = None
    variety: str | None = None
    soil_type: str | None = None
    target_yield: float = 0.0

    source: str = "manual"
    import_batch_id: UUID | None = None
    is_trained: bool = False

    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
