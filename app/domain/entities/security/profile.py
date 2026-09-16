from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Profile:
    id: int = 0
    user_id: int = 0
    first_name: str = ""
    last_name: str = ""
    phone: str | None = None
    age: int | None = None
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
