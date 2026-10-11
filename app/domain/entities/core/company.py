from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Company:
    id: int = 0
    code: str = ""
    name: str = ""
    ruc: str | None = None
    description: str | None = None
    logo_path: str | None = None
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
