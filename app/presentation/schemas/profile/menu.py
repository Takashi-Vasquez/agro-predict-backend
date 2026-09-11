from pydantic import ConfigDict, Field

from app.presentation.schemas import BaseReadSchema


class MenuRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    parent_id: int | None = Field(default=None, alias="parentId")
    name: str = Field(alias="name")
    icon: str | None = Field(default=None, alias="icon")
    route: str | None = Field(default=None, alias="route")
    order_index: int = Field(alias="orderIndex")
    badge: str | None = Field(default=None, alias="badge")
    status: str


class PermissionRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    code: str = Field(alias="code")
    name: str = Field(alias="name")


class MenuTreeRead(MenuRead):
    children: list["MenuTreeRead"] = Field(default=[], alias="children")
    available_permissions: list[PermissionRead] = Field(default=[], alias="availablePermissions")
