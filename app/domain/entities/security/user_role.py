from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UserRole:
    id: int = 0
    user_id: int = 0
    role_id: int = 0
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
