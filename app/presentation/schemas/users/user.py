from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.presentation.schemas import BaseReadSchema


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=6, max_length=128)


class UserRead(UserBase, BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    status: str
    is_admin: bool = Field(alias="isAdmin")
    created_at: datetime
