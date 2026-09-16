from pydantic import BaseModel, ConfigDict, Field


class RoleMenuPermissionCreate(BaseModel):
    role_id: int = Field(alias="roleId")
    menu_id: int = Field(alias="menuId")
    permission_id: int = Field(alias="permissionId")


class RoleMenuPermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    role_id: int = Field(alias="roleId")
    menu_id: int = Field(alias="menuId")
    permission_id: int = Field(alias="permissionId")


class MenuPermissionAssignment(BaseModel):
    menu_id: int = Field(alias="menuId")
    permission_id: int = Field(alias="permissionId")


class RoleMenuPermissionBulkCreate(BaseModel):
    assignments: list[MenuPermissionAssignment]


class RoleMenuPermissionSyncRequest(BaseModel):
    assignments: list[MenuPermissionAssignment]
