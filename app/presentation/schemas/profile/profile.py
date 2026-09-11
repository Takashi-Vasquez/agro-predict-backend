from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema


class ProfileBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    age: int | None = Field(default=None, ge=0, le=150)


class ProfileCreate(ProfileBase):
    user_id: int


class ProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = None
    age: int | None = None


class ProfileRead(ProfileBase, BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    user_id: int = Field(alias="userId")
    status: str
    created_at: datetime
    updated_at: datetime
