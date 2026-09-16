from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema


class CropBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    variety: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)
    cycle: int = Field(ge=0)
    temperature: str = Field(min_length=1, max_length=50)
    water: str = Field(min_length=1, max_length=100)
    color: str = Field(min_length=1, max_length=20)


class CropCreate(CropBase):
    pass


class CropUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    variety: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    cycle: int | None = Field(default=None, ge=0)
    temperature: str | None = Field(default=None, min_length=1, max_length=50)
    water: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, min_length=1, max_length=20)


class CropRead(CropBase, BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    owner_id: int = Field(alias="ownerId")
    status: str
    created_at: datetime
    updated_at: datetime
