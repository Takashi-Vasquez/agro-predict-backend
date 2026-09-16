from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Crop:
    id: int = 0
    owner_id: int = 0
    name: str = ""
    variety: str = ""
    category: str = ""
    cycle: int = 0
    temperature: str = ""
    water: str = ""
    color: str = ""
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
