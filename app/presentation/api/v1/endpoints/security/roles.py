from fastapi import APIRouter

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.schemas.roles.role import RoleCreate, RoleRead, RoleUpdate
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.repositories.role_repository import RoleRepositoryImpl
from app.domain.exceptions import AppException
from app.domain.use_cases.roles.create_role import CreateRoleUseCase
from app.domain.use_cases.roles.list_roles import ListRolesUseCase
from app.domain.use_cases.roles.update_role import UpdateRoleUseCase
from app.domain.use_cases.roles.delete_role import DeleteRoleUseCase

router = APIRouter(prefix="/roles", tags=["roles"])


def _require_admin(user: CurrentUser) -> None:
    if not user.is_admin:
        raise AppException.forbidden("Se requieren permisos de administrador")


@router.get("")
def list_roles(user: CurrentUser, db: DbDep):
    _require_admin(user)
    role_repo = RoleRepositoryImpl(db)
    roles = ListRolesUseCase(role_repo).execute()
    data = [RoleRead.model_validate(r).model_dump() for r in roles]
    return ApiResponseFactory.ok(data, "Roles obtenidos correctamente")


@router.post("")
def create_role(data: RoleCreate, user: CurrentUser, db: DbDep):
    _require_admin(user)
    role_repo = RoleRepositoryImpl(db)
    try:
        role = CreateRoleUseCase(role_repo).execute(name=data.name, description=data.description)
    except ValueError as exc:
        raise AppException.conflict(str(exc))
    result = RoleRead.model_validate(role).model_dump()
    return ApiResponseFactory.created(result, "Rol creado correctamente")


@router.get("/{role_id}")
def get_role(role_id: int, user: CurrentUser, db: DbDep):
    _require_admin(user)
    role = RoleRepositoryImpl(db).get(role_id)
    if not role:
        raise AppException.not_found("Rol no encontrado")
    data = RoleRead.model_validate(role).model_dump()
    return ApiResponseFactory.ok(data, "Rol obtenido correctamente")


@router.patch("/{role_id}")
def update_role(role_id: int, data: RoleUpdate, user: CurrentUser, db: DbDep):
    _require_admin(user)
    role_repo = RoleRepositoryImpl(db)
    try:
        role = UpdateRoleUseCase(role_repo).execute(role_id, **data.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise AppException.not_found(str(exc))
    result = RoleRead.model_validate(role).model_dump()
    return ApiResponseFactory.ok(result, "Rol actualizado correctamente")


@router.delete("/{role_id}")
def delete_role(role_id: int, user: CurrentUser, db: DbDep):
    _require_admin(user)
    try:
        DeleteRoleUseCase(RoleRepositoryImpl(db)).execute(role_id)
    except ValueError as exc:
        raise AppException.not_found(str(exc))
    return ApiResponseFactory.no_content("Rol eliminado correctamente")
