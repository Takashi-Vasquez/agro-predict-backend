from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RoleMenuPermissionCreate(BaseModel):
    role_id: int
    menu_id: int
    permission_id: int


class RoleMenuPermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    menu_id: int
    permission_id: int
    status: str
    created_at: datetime


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    first_name: str
    last_name: str
    phone: str | None = None
    age: int | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class UserWithProfileCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = None
    age: int | None = None
    role_ids: list[int] = []


class UserWithProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    status: str
    is_admin: bool
    created_at: datetime
    profile: ProfileRead | None = None
    roles: list[RoleRead] = []
