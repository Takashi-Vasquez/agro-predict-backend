from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema


class RolePermissionRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    status: str


class RoleMenuTreeNodeRead(BaseReadSchema):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    parent_id: int | None = Field(default=None, alias="parentId")
    code: str
    name: str
    permissions: list[int] = Field(default=[], alias="permissions")
    children: list["RoleMenuTreeNodeRead"] = Field(default=[], alias="children")


class RolePermissionTreeRead(BaseReadSchema):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    status: str
    menus: list[RoleMenuTreeNodeRead] = Field(default=[], alias="menus")


class RolePermissionCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=100)
    status: str = Field(default="ACTIVE")
    menus: list[RoleMenuTreeNodeRead] = Field(default=[], alias="menus")


class RolePermissionUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    status: str | None = None
    menus: list[RoleMenuTreeNodeRead] | None = Field(default=None, alias="menus")
