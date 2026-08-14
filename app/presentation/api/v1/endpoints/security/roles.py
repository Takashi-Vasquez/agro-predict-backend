from fastapi import APIRouter, HTTPException, status

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.schemas.roles.role import RoleCreate, RoleRead, RoleUpdate
from app.infrastructure.repositories.role_repository import RoleRepositoryImpl
from app.domain.use_cases.roles.create_role import CreateRoleUseCase
from app.domain.use_cases.roles.list_roles import ListRolesUseCase
from app.domain.use_cases.roles.update_role import UpdateRoleUseCase
from app.domain.use_cases.roles.delete_role import DeleteRoleUseCase

router = APIRouter(prefix="/roles", tags=["roles"])


def _require_admin(user: CurrentUser) -> None:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )


@router.get("", response_model=list[RoleRead])
def list_roles(user: CurrentUser, db: DbDep) -> list[RoleRead]:
    _require_admin(user)
    role_repo = RoleRepositoryImpl(db)
    roles = ListRolesUseCase(role_repo).execute()
    return [RoleRead.model_validate(r) for r in roles]


@router.post("", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(data: RoleCreate, user: CurrentUser, db: DbDep) -> RoleRead:
    _require_admin(user)
    role_repo = RoleRepositoryImpl(db)
    try:
        role = CreateRoleUseCase(role_repo).execute(name=data.name, description=data.description)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return RoleRead.model_validate(role)


@router.get("/{role_id}", response_model=RoleRead)
def get_role(role_id: int, user: CurrentUser, db: DbDep) -> RoleRead:
    _require_admin(user)
    role = RoleRepositoryImpl(db).get(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    return RoleRead.model_validate(role)


@router.patch("/{role_id}", response_model=RoleRead)
def update_role(role_id: int, data: RoleUpdate, user: CurrentUser, db: DbDep) -> RoleRead:
    _require_admin(user)
    role_repo = RoleRepositoryImpl(db)
    try:
        role = UpdateRoleUseCase(role_repo).execute(role_id, **data.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return RoleRead.model_validate(role)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, user: CurrentUser, db: DbDep) -> None:
    _require_admin(user)
    try:
        DeleteRoleUseCase(RoleRepositoryImpl(db)).execute(role_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
