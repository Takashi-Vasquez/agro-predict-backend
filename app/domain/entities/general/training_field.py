from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TrainingField:
    id: int
    field_key: str
    label: str
    field_type: str
    category: str
    unit: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: Optional[list[str]] = None
    is_required: bool = True
    order_index: int = 0
    status: str = "ACTIVE"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None