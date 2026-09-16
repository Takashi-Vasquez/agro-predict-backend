from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Weather:
    id: int = 0
    crop_id: int | None = None
    location: str = ""
    temperature: float = 0.0
    humidity: float = 0.0
    wind_speed: float = 0.0
    wind_direction: str | None = None
    precipitation: float = 0.0
    pressure: float = 0.0
    recorded_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
