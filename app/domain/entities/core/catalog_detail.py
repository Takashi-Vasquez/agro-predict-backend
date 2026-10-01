from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CatalogDetail:
    id: int = 0
    catalog_id: int = 0
    value: str = ""
    label: str = ""
    order_index: int = 0
    is_active: bool = True
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
