from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Role:
    id: int = 0
    name: str = ""
    description: str | None = None
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
