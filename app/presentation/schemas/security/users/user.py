from pydantic import BaseModel, EmailStr, Field

from app.presentation.schemas import BaseReadSchema


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    is_admin: bool = Field(default=False, alias="isAdmin")


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_admin: bool | None = Field(default=None, alias="isAdmin")


class UserRead(BaseReadSchema):
    id: int
    email: EmailStr
    is_admin: bool = Field(alias="isAdmin")
    status: str
