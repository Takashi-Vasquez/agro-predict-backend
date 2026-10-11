from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UserCompany:
    id: int = 0
    user_id: int = 0
    company_id: int = 0
    is_default: bool = False
    is_active: bool = False
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
