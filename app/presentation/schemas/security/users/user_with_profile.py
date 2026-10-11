from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.infrastructure.config.security import PASSWORD_SENTINEL
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


class CompanyCreateItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="id")
    is_default: bool = Field(default=False, alias="isDefault")


class UserWithProfileCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    status: Literal["ACTIVE", "INACTIVE"] = "ACTIVE"
    document_number: str | None = Field(default=None, alias="documentNumber", max_length=30)
    first_name: str = Field(min_length=1, max_length=100, alias="firstName")
    last_name: str = Field(min_length=1, max_length=100, alias="lastName")
    phone: str | None = Field(default=None, alias="phone")
    age: int | None = Field(default=None, alias="age")
    role_ids: list[int] = Field(default=[], alias="roleIds")
    companies: list[CompanyCreateItem] = Field(default=[], alias="companies")


class UserWithProfileUpdate(BaseModel):
    email: EmailStr | None = Field(default=None, alias="email")
    password: str | None = Field(default=None, max_length=128)
    change_password: bool = Field(default=False, alias="changePassword")
    status: Literal["ACTIVE", "INACTIVE"] | None = Field(default=None, alias="status")
    first_name: str | None = Field(default=None, alias="firstName", min_length=1, max_length=100)
    last_name: str | None = Field(default=None, alias="lastName", min_length=1, max_length=100)
    phone: str | None = Field(default=None, alias="phone")
    age: int | None = Field(default=None, alias="age")
    document_number: str | None = Field(default=None, alias="documentNumber", max_length=30)
    role_ids: list[int] = Field(default=[], alias="roleIds")
    companies: list[CompanyCreateItem] = Field(default=[], alias="companies")


class UserWithProfileRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    email: str = Field(alias="email")
    password: str = Field(default=PASSWORD_SENTINEL)
    status: str
    is_admin: bool = Field(alias="isAdmin")
    created_at: datetime
    document_number: str | None = Field(default=None, alias="documentNumber")
    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    phone: str | None = Field(default=None, alias="phone")
    age: int | None = Field(default=None, alias="age")
    role_ids: list[int] = Field(default=[], alias="roleIds")
    companies: list[CompanyCreateItem] = Field(default=[], alias="companies")
