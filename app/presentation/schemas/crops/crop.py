from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CropBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    location: str | None = None
    area_hectares: float = Field(default=0.0, ge=0)
    notes: str | None = Field(default=None, max_length=500)


class CropCreate(CropBase):
    pass


class CropUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = None
    area_hectares: float | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=500)


class CropRead(CropBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    status: str
    created_at: datetime
    updated_at: datetime
