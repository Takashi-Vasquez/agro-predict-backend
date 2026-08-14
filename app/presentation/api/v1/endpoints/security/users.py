from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from app.presentation.api.deps import CurrentUser, DbDep
from app.infrastructure.orm.security.user import User
from app.infrastructure.repositories.user_repository import UserRepositoryImpl
from app.infrastructure.repositories.profile_repository import ProfileRepositoryImpl
from app.infrastructure.repositories.role_repository import RoleRepositoryImpl
from app.infrastructure.repositories.user_role_repository import UserRoleRepositoryImpl
from app.presentation.schemas.profile.profile import ProfileRead, ProfileUpdate
from app.presentation.schemas.roles.role import RoleRead
from app.presentation.schemas.users.user_with_profile import UserWithProfileCreate, UserWithProfileRead
from app.domain.use_cases.users.create_user import CreateUserUseCase
from app.domain.use_cases.users.list_users import ListUsersUseCase
from app.domain.use_cases.users.delete_user import DeleteUserUseCase
from app.infrastructure.config.security import hash_password
from app.infrastructure.orm.security.user_role import UserRole as UserRoleModel

router = APIRouter(prefix="/users", tags=["users"])


def _require_admin(user: CurrentUser) -> None:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )


@router.get("", response_model=list[UserWithProfileRead])
def list_users(user: CurrentUser, db: DbDep) -> list[UserWithProfileRead]:
    _require_admin(user)
    user_repo = UserRepositoryImpl(db)
    use_case = ListUsersUseCase(user_repo)
    users = use_case.execute()
    return [_build_user_read(u, db) for u in users]


@router.post("", response_model=UserWithProfileRead, status_code=status.HTTP_201_CREATED)
def create_user(data: UserWithProfileCreate, user: CurrentUser, db: DbDep) -> UserWithProfileRead:
    _require_admin(user)
    user_repo = UserRepositoryImpl(db)
    use_case = CreateUserUseCase(user_repo)
    try:
        created_user = use_case.execute(
            email=data.email,
            hashed_password=hash_password(data.password),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

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

    return _build_user_read(db.get(User, created_user.id), db)


@router.get("/{user_id}", response_model=UserWithProfileRead)
def get_user(user_id: int, user: CurrentUser, db: DbDep) -> UserWithProfileRead:
    _require_admin(user)
    user_repo = UserRepositoryImpl(db)
    target = user_repo.get(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return _build_user_read(db.get(User, user_id), db)


@router.patch("/{user_id}", response_model=UserWithProfileRead)
def update_user(
    user_id: int,
    data: ProfileUpdate,
    user: CurrentUser,
    db: DbDep,
) -> UserWithProfileRead:
    _require_admin(user)
    target = UserRepositoryImpl(db).get(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
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
    return _build_user_read(db.get(User, user_id), db)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, user: CurrentUser, db: DbDep) -> None:
    _require_admin(user)
    target = UserRepositoryImpl(db).get(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    DeleteUserUseCase(UserRepositoryImpl(db)).execute(user_id)


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
