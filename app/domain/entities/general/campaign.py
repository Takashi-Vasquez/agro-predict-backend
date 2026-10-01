from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Campaign:
    id: int = 0
    user_id: int = 0
    code: str = ""
    name: str = ""
    start_date: date = field(default_factory=date.today)
    end_date: date = field(default_factory=date.today)
    crop_id: int = 0
    crop_name: str = ""
    status: str = "PLANIFICADA"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
