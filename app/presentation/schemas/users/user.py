from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=6, max_length=128)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    is_admin: bool
    created_at: datetime
