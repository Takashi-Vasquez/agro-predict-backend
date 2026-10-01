from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Catalog:
    id: int = 0
    code: str = ""
    label: str = ""
    description: str | None = None
    is_active: bool = True
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
