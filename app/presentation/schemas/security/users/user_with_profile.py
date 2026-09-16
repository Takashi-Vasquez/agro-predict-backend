from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.presentation.schemas import BaseReadSchema


class RoleMenuPermissionCreate(BaseModel):
    role_id: int = Field(alias="roleId")
    menu_id: int = Field(alias="menuId")
    permission_id: int = Field(alias="permissionId")


class RoleMenuPermissionRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    role_id: int = Field(alias="roleId")
    menu_id: int = Field(alias="menuId")
    permission_id: int = Field(alias="permissionId")
    status: str
    created_at: datetime


class ProfileRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    user_id: int = Field(alias="userId")
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    phone: str | None = Field(default=None, alias="phone")
    age: int | None = Field(default=None, alias="age")
    status: str
    created_at: datetime
    updated_at: datetime


class RoleRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    name: str = Field(alias="name")
    description: str | None = Field(default=None, alias="description")
    status: str
    created_at: datetime
    updated_at: datetime


class UserWithProfileCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    first_name: str = Field(min_length=1, max_length=100, alias="firstName")
    last_name: str = Field(min_length=1, max_length=100, alias="lastName")
    phone: str | None = Field(default=None, alias="phone")
    age: int | None = Field(default=None, alias="age")
    role_ids: list[int] = Field(default=[], alias="roleIds")


class UserWithProfileRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    email: str = Field(alias="email")
    status: str
    is_admin: bool = Field(alias="isAdmin")
    created_at: datetime
    profile: ProfileRead | None = Field(default=None, alias="profile")
    roles: list[RoleRead] = Field(default=[], alias="roles")
