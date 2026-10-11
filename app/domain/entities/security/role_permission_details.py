from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RolePermissionDetail:
    id: int = 0
    role_permissions_id: int = 0
    menu_id: int = 0
    permission_id: int = 0
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
