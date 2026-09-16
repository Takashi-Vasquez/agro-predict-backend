from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Menu:
    id: int = 0
    code: str = ""
    parent_id: int | None = None
    name: str = ""
    icon: str | None = None
    route: str | None = None
    order_index: int = 0
    badge: str | None = None
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
