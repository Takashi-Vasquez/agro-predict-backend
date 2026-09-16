from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MenuPermission:
    id: int = 0
    menu_id: int = 0
    permission_id: int = 0
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
