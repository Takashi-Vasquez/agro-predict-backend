from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema


class RoleRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    name: str = Field(alias="name")
    description: str | None = Field(default=None, alias="description")
    status: str
    created_at: datetime
    updated_at: datetime


class PermissionRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    code: str = Field(alias="code")
    name: str = Field(alias="name")


class MenuRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    parent_id: int | None = Field(default=None, alias="parentId")
    name: str = Field(alias="name")
    code: str = Field(alias="code")
    icon: str | None = Field(default=None, alias="icon")
    route: str | None = Field(default=None, alias="route")
    order_index: int = Field(alias="orderIndex")
    badge: str | None = Field(default=None, alias="badge")
    status: str


class MenuTreeRead(MenuRead):
    children: list["MenuTreeRead"] = Field(default=[], alias="children")
    permissions: list[str] = Field(default=[], alias="permissions")


class UserMeRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    email: str = Field(alias="email")
    status: str
    is_admin: bool = Field(alias="isAdmin")

    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    full_name: str | None = Field(default=None, alias="fullName")
    phone: str | None = Field(default=None, alias="phone")
    age: int | None = Field(default=None, alias="age")

    roles: list[RoleRead] = Field(alias="roles")
    menus: list[MenuTreeRead] = Field(alias="menus")
