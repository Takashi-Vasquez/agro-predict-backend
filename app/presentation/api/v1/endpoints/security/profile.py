from fastapi import APIRouter, HTTPException, status

from app.presentation.api.deps import CurrentUser, DbDep
from app.infrastructure.repositories.menu_repository import MenuRepositoryImpl
from app.infrastructure.repositories.menu_permission_repository import MenuPermissionRepositoryImpl
from app.infrastructure.repositories.permission_repository import PermissionRepositoryImpl
from app.infrastructure.repositories.role_menu_permission_repository import RoleMenuPermissionRepositoryImpl
from app.infrastructure.repositories.role_repository import RoleRepositoryImpl
from app.presentation.schemas.profile.menu import MenuTreeRead
from app.presentation.schemas.profile.permission import PermissionRead
from app.presentation.schemas.profile.role_menu_permission import (
    RoleMenuPermissionBulkCreate,
    RoleMenuPermissionCreate,
    RoleMenuPermissionRead,
)
from app.domain.use_cases.permissions.assign_permission import AssignPermissionUseCase
from app.domain.use_cases.permissions.list_role_permissions import ListRolePermissionsUseCase
from app.domain.use_cases.permissions.remove_permission import RemovePermissionUseCase
from app.domain.use_cases.permissions.sync_role_permissions import SyncRolePermissionsUseCase

router = APIRouter(prefix="/profile", tags=["profile"])


def _require_admin(user: CurrentUser) -> None:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )


@router.get("/menus", response_model=list[MenuTreeRead])
def list_menus(user: CurrentUser, db: DbDep) -> list[MenuTreeRead]:
    _require_admin(user)
    menu_repo = MenuRepositoryImpl(db)
    mp_repo = MenuPermissionRepositoryImpl(db)
    roots = menu_repo.get_root_menus()
    return [_build_menu_tree_entity(m, menu_repo, mp_repo) for m in roots]


@router.get("/permissions", response_model=list[PermissionRead])
def list_permissions(user: CurrentUser, db: DbDep) -> list[PermissionRead]:
    _require_admin(user)
    perms = PermissionRepositoryImpl(db).get_all()
    return [PermissionRead.model_validate(p) for p in perms]


@router.post("/role-permissions", response_model=RoleMenuPermissionRead, status_code=status.HTTP_201_CREATED)
def assign_permission(
    data: RoleMenuPermissionCreate,
    user: CurrentUser,
    db: DbDep,
) -> RoleMenuPermissionRead:
    _require_admin(user)
    use_case = AssignPermissionUseCase(
        rmp_repo=RoleMenuPermissionRepositoryImpl(db),
        role_repo=RoleRepositoryImpl(db),
        menu_repo=MenuRepositoryImpl(db),
        perm_repo=PermissionRepositoryImpl(db),
    )
    try:
        rmp = use_case.execute(data.role_id, data.menu_id, data.permission_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return RoleMenuPermissionRead.model_validate(rmp)


@router.put("/role-permissions/{role_id}", response_model=list[RoleMenuPermissionRead])
def sync_role_permissions(
    role_id: int,
    data: RoleMenuPermissionBulkCreate,
    user: CurrentUser,
    db: DbDep,
) -> list[RoleMenuPermissionRead]:
    _require_admin(user)
    use_case = SyncRolePermissionsUseCase(
        rmp_repo=RoleMenuPermissionRepositoryImpl(db),
        role_repo=RoleRepositoryImpl(db),
    )
    try:
        assignments = [(a.menu_id, a.permission_id) for a in data.assignments]
        rmps = use_case.execute(role_id, assignments)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return [RoleMenuPermissionRead.model_validate(r) for r in rmps]


@router.get("/role-permissions/{role_id}", response_model=list[RoleMenuPermissionRead])
def list_role_permissions(role_id: int, user: CurrentUser, db: DbDep) -> list[RoleMenuPermissionRead]:
    _require_admin(user)
    rmps = ListRolePermissionsUseCase(RoleMenuPermissionRepositoryImpl(db)).execute(role_id)
    return [RoleMenuPermissionRead.model_validate(r) for r in rmps]


@router.delete("/role-permissions/{rmp_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_permission(rmp_id: int, user: CurrentUser, db: DbDep) -> None:
    _require_admin(user)
    try:
        RemovePermissionUseCase(RoleMenuPermissionRepositoryImpl(db)).execute(rmp_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


def _build_menu_tree_entity(menu, menu_repo, mp_repo) -> MenuTreeRead:
    from app.domain.entities import Menu as MenuEntity

    menu_entity = MenuEntity(
        id=menu.id, parent_id=menu.parent_id, name=menu.name, icon=menu.icon,
        route=menu.route, order_index=menu.order_index, status=menu.status,
    )
    children = menu_repo.get_children(menu.id)
    perms = mp_repo.get_permissions_by_menu_id(menu.id)
    return MenuTreeRead(
        id=menu_entity.id,
        parent_id=menu_entity.parent_id,
        name=menu_entity.name,
        icon=menu_entity.icon,
        route=menu_entity.route,
        order_index=menu_entity.order_index,
        status=menu_entity.status,
        children=[_build_menu_tree_entity(c, menu_repo, mp_repo) for c in children],
        available_permissions=[PermissionRead.model_validate(p) for p in perms],
    )
