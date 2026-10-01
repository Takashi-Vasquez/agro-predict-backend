from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class TrainingFieldRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    field_key: str = Field(alias="fieldKey")
    label: str
    field_type: str = Field(alias="fieldType")
    category: str
    unit: Optional[str] = None
    min_value: Optional[float] = Field(alias="minValue", default=None)
    max_value: Optional[float] = Field(alias="maxValue", default=None)
    options: Optional[list[str]] = None
    is_required: bool = Field(alias="isRequired")
    order_index: int = Field(alias="orderIndex")