from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

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


class AssignmentItem(BaseModel):
    menu_id: int = Field(alias="menuId")
    permission_id: int = Field(alias="permissionId")


class RoleMenuPermissionBulkCreate(BaseModel):
    assignments: list[AssignmentItem]
