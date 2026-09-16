from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Permission:
    id: int = 0
    code: str = ""
    name: str = ""
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
