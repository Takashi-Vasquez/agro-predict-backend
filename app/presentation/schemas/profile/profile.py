from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
