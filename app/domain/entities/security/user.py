from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    id: int = 0
    email: str = ""
    hashed_password: str = ""
    is_admin: bool = False
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
