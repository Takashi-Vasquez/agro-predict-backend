from fastapi import APIRouter

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.repositories.security.menu_repository import MenuRepositoryImpl
from app.infrastructure.repositories.security.menu_permission_repository import MenuPermissionRepositoryImpl
from app.infrastructure.repositories.security.permission_repository import PermissionRepositoryImpl
from app.infrastructure.repositories.security.role_permission_repository import RolePermissionRepositoryImpl
from app.presentation.schemas.security.menu.menu import MenuTreeRead
from app.presentation.schemas.security.permission.permission import PermissionRead
from app.presentation.schemas.security.access_profile.access_profile import (
    RolePermissionCreate,
    RolePermissionRead,
    RolePermissionTreeRead,
    RolePermissionUpdate,
    RoleMenuTreeNodeRead,
)
from app.domain.exceptions import AppException
from app.domain.use_cases.security.permissions.list_role_permissions import ListRolePermissionsUseCase
from app.domain.use_cases.security.permissions.sync_role_permissions import SyncRolePermissionsUseCase

router = APIRouter(prefix="/security/access-profile", tags=["Security/AccessProfile"])


@router.get("/menus")
def list_menus(user: CurrentUser, db: DbDep):
    menu_repo = MenuRepositoryImpl(db)
    mp_repo = MenuPermissionRepositoryImpl(db)
    all_menus = menu_repo.get_all()
    perms_by_menu = mp_repo.get_permissions_by_menu_ids([m.id for m in all_menus])
    children_map = _group_children(all_menus)
    data = [
        _build_menu_tree_entity(m, children_map, perms_by_menu).model_dump()
        for m in children_map.get(None, [])
    ]
    return ApiResponseFactory.ok(data, "Menús obtenidos correctamente")


@router.get("/permissions")
def list_permissions(user: CurrentUser, db: DbDep):
    perms = PermissionRepositoryImpl(db).get_all()
    data = [PermissionRead.model_validate(p).model_dump() for p in perms]
    return ApiResponseFactory.ok(data, "Permisos obtenidos correctamente")


@router.get("/role-permissions")
def list_role_permissions(user: CurrentUser, db: DbDep):
    roles = RolePermissionRepositoryImpl(db).list(limit=1000)
    data = [RolePermissionRead.model_validate(r).model_dump() for r in roles]
    return ApiResponseFactory.ok(data, "Roles obtenidos correctamente")


@router.get("/role-permissions/{role_id}")
def get_role_permission(role_id: int, user: CurrentUser, db: DbDep):
    role_repo = RolePermissionRepositoryImpl(db)
    role = role_repo.get(role_id)
    if not role:
        raise AppException.not_found("Rol no encontrado")
    data = _build_role_tree_response(role, role_repo)
    return ApiResponseFactory.ok(data, "Rol obtenido correctamente")


@router.post("/role-permissions")
def create_role_permission(data: RolePermissionCreate, user: CurrentUser, db: DbDep):
    role_repo = RolePermissionRepositoryImpl(db)
    if role_repo.get_by_name(data.name):
        raise AppException.conflict("Ya existe un rol con ese nombre")
    assignments = _flatten_assignments(data.menus)
    role = role_repo.create(name=data.name, company_id=None, status=data.status)
    SyncRolePermissionsUseCase(role_repo).execute(role.id, assignments)
    result = _build_role_tree_response(role_repo.get(role.id), role_repo)
    return ApiResponseFactory.created(result, "Rol creado correctamente")


@router.patch("/role-permissions/{role_id}")
def update_role_permission(
    role_id: int,
    data: RolePermissionUpdate,
    user: CurrentUser,
    db: DbDep,
):
    role_repo = RolePermissionRepositoryImpl(db)
    role = role_repo.get(role_id)
    if not role:
        raise AppException.not_found("Rol no encontrado")

    payload = data.model_dump(exclude_unset=True)

    if payload.get("name"):
        existing = role_repo.get_by_name(payload["name"])
        if existing and existing.id != role_id:
            raise AppException.conflict("Ya existe un rol con ese nombre")
        role = role_repo.update(role, name=payload["name"])

    if payload.get("status"):
        role = role_repo.update(role, status=payload["status"])

    if "menus" in payload and data.menus is not None:
        assignments = _flatten_assignments(data.menus)
        SyncRolePermissionsUseCase(role_repo).execute(role_id, assignments)

    result = _build_role_tree_response(role_repo.get(role_id), role_repo)
    return ApiResponseFactory.ok(result, "Rol actualizado correctamente")


@router.delete("/role-permissions/{role_id}")
def delete_role_permission(role_id: int, user: CurrentUser, db: DbDep):
    role_repo = RolePermissionRepositoryImpl(db)
    role = role_repo.get(role_id)
    if not role:
        raise AppException.not_found("Rol no encontrado")
    role_repo.delete(role)
    return ApiResponseFactory.no_content("Rol eliminado correctamente")


def _group_children(all_menus) -> dict:
    children_map: dict = {}
    for m in all_menus:
        children_map.setdefault(m.parent_id, []).append(m)
    return children_map


def _build_role_tree_response(role, role_repo) -> dict:
    details = ListRolePermissionsUseCase(role_repo).execute(role.id)
    granted: dict[int, list[int]] = {}
    for d in details:
        granted.setdefault(d.menu_id, []).append(d.permission_id)
    menu_repo = MenuRepositoryImpl(role_repo.db)
    all_menus = menu_repo.get_all()
    children_map = _group_children(all_menus)
    menus = [
        _build_role_menu_tree(m, children_map, granted).model_dump()
        for m in children_map.get(None, [])
    ]
    return RolePermissionTreeRead(
        id=role.id,
        name=role.name,
        status=role.status,
        menus=menus,
    ).model_dump()


def _flatten_assignments(nodes) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for node in nodes or []:
        for permission_id in node.permissions:
            result.append((node.id, permission_id))
        result.extend(_flatten_assignments(node.children))
    return result


def _build_role_menu_tree(menu, children_map, granted: dict[int, list[int]]) -> RoleMenuTreeNodeRead:
    return RoleMenuTreeNodeRead(
        id=menu.id,
        parent_id=menu.parent_id,
        code=menu.code,
        name=menu.name,
        permissions=granted.get(menu.id, []),
        children=[
            _build_role_menu_tree(c, children_map, granted)
            for c in children_map.get(menu.id, [])
        ],
    )


def _build_menu_tree_entity(menu, children_map, perms_by_menu) -> MenuTreeRead:
    return MenuTreeRead(
        id=menu.id,
        parent_id=menu.parent_id,
        code=menu.code,
        name=menu.name,
        icon=menu.icon,
        route=menu.route,
        order_index=menu.order_index,
        badge=menu.badge,
        status=menu.status,
        children=[
            _build_menu_tree_entity(c, children_map, perms_by_menu)
            for c in children_map.get(menu.id, [])
        ],
        permissions=[
            PermissionRead.model_validate(p) for p in perms_by_menu.get(menu.id, [])
        ],
    )
