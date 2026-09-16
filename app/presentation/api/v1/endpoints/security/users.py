from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.orm.security.user import User
from app.infrastructure.repositories.security.user_repository import UserRepositoryImpl
from app.infrastructure.repositories.security.profile_repository import ProfileRepositoryImpl
from app.infrastructure.repositories.security.role_repository import RoleRepositoryImpl
from app.infrastructure.repositories.security.user_role_repository import UserRoleRepositoryImpl
from app.presentation.schemas.security.profile.profile import ProfileRead, ProfileUpdate
from app.presentation.schemas.security.roles.role import RoleRead
from app.presentation.schemas.security.users.user_with_profile import UserWithProfileCreate, UserWithProfileRead
from app.domain.exceptions import AppException
from app.domain.use_cases.security.users.create_user import CreateUserUseCase
from app.domain.use_cases.security.users.list_users import ListUsersUseCase
from app.domain.use_cases.security.users.delete_user import DeleteUserUseCase
from app.infrastructure.config.security import hash_password
from app.infrastructure.orm.security.user_role import UserRole as UserRoleModel

router = APIRouter(prefix="/security/users", tags=["Security/Users"])


def _require_admin(user: CurrentUser) -> None:
    if not user.is_admin:
        raise AppException.forbidden("Se requieren permisos de administrador")


@router.get("")
def list_users(user: CurrentUser, db: DbDep):
    _require_admin(user)
    user_repo = UserRepositoryImpl(db)
    use_case = ListUsersUseCase(user_repo)
    users = use_case.execute()
    data = [_build_user_read(u, db).model_dump() for u in users]
    return ApiResponseFactory.ok(data, "Usuarios obtenidos correctamente")


@router.post("")
def create_user(data: UserWithProfileCreate, user: CurrentUser, db: DbDep):
    _require_admin(user)
    user_repo = UserRepositoryImpl(db)
    use_case = CreateUserUseCase(user_repo)
    try:
        created_user = use_case.execute(
            email=data.email,
            hashed_password=hash_password(data.password),
        )
    except ValueError as exc:
        raise AppException.conflict(str(exc))

    profile_repo = ProfileRepositoryImpl(db)
    profile_repo.create(
        user_id=created_user.id,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        age=data.age,
    )

    if data.role_ids:
        for role_id in data.role_ids:
            db.add(UserRoleModel(user_id=created_user.id, role_id=role_id))
        db.commit()

    result = _build_user_read(db.get(User, created_user.id), db).model_dump()
    return ApiResponseFactory.created(result, "Usuario creado correctamente")


@router.get("/{user_id}")
def get_user(user_id: int, user: CurrentUser, db: DbDep):
    _require_admin(user)
    user_repo = UserRepositoryImpl(db)
    target = user_repo.get(user_id)
    if not target:
        raise AppException.not_found("Usuario no encontrado")
    data = _build_user_read(db.get(User, user_id), db).model_dump()
    return ApiResponseFactory.ok(data, "Usuario obtenido correctamente")


@router.patch("/{user_id}")
def update_user(
    user_id: int,
    data: ProfileUpdate,
    user: CurrentUser,
    db: DbDep,
):
    _require_admin(user)
    target = UserRepositoryImpl(db).get(user_id)
    if not target:
        raise AppException.not_found("Usuario no encontrado")
    profile_repo = ProfileRepositoryImpl(db)
    profile = profile_repo.get_by_user_id(user_id)
    if profile:
        from app.domain.entities import Profile as ProfileEntity
        profile_entity = ProfileEntity(
            id=profile.id, user_id=profile.user_id, first_name=profile.first_name,
            last_name=profile.last_name, phone=profile.phone, age=profile.age,
            status=profile.status, created_at=profile.created_at, updated_at=profile.updated_at,
        )
        profile_repo.update(profile_entity, **data.model_dump(exclude_unset=True))
    result = _build_user_read(db.get(User, user_id), db).model_dump()
    return ApiResponseFactory.ok(result, "Usuario actualizado correctamente")


@router.delete("/{user_id}")
def delete_user(user_id: int, user: CurrentUser, db: DbDep):
    _require_admin(user)
    target = UserRepositoryImpl(db).get(user_id)
    if not target:
        raise AppException.not_found("Usuario no encontrado")
    DeleteUserUseCase(UserRepositoryImpl(db)).execute(user_id)
    return ApiResponseFactory.no_content("Usuario eliminado correctamente")


def _build_user_read(user: User, db: Session) -> UserWithProfileRead:
    orm = db.get(User, user.id)
    profile = ProfileRepositoryImpl(db).get_by_user_id(user.id)
    roles = [ur.role for ur in orm.user_roles] if orm and orm.user_roles else []
    return UserWithProfileRead(
        id=user.id,
        email=user.email,
        status=user.status,
        is_admin=user.is_admin,
        created_at=user.created_at,
        profile=ProfileRead.model_validate(profile) if profile else None,
        roles=[RoleRead.model_validate(r) for r in roles],
    )
