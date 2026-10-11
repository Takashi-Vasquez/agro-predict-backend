from fastapi import APIRouter

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.repositories.security.user_repository import UserRepositoryImpl
from app.infrastructure.repositories.security.profile_repository import ProfileRepositoryImpl
from app.infrastructure.repositories.security.role_permission_repository import RolePermissionRepositoryImpl
from app.presentation.schemas.security.users.user_with_profile import (
    UserWithProfileCreate,
    UserWithProfileRead,
    UserWithProfileUpdate,
)
from app.domain.exceptions import AppException
from app.domain.use_cases.security.users.create_user import CreateUserUseCase
from app.domain.use_cases.security.users.update_user import UpdateUserUseCase
from app.domain.use_cases.security.users.list_users import ListUsersUseCase
from app.domain.use_cases.security.users.get_user import GetUserUseCase
from app.domain.use_cases.security.users.delete_user import DeleteUserUseCase
from app.infrastructure.config.security import PASSWORD_SENTINEL, hash_password
from app.infrastructure.orm.security.user_role import UserRole as UserRoleModel
from app.infrastructure.orm.security.user_company import UserCompany as UserCompanyModel
from app.infrastructure.repositories.core.company_repository import CompanyRepositoryImpl

router = APIRouter(prefix="/security/users", tags=["Security/Users"])


def _sync_user_roles(db, user_id: int, role_ids: list[int]) -> None:
    """Upsert + soft delete de roles: conserva filas existentes."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    existing = {
        r.role_id: r
        for r in db.query(UserRoleModel).filter(UserRoleModel.user_id == user_id).all()
    }
    desired = set(role_ids)
    for rid, row in existing.items():
        if rid in desired:
            if row.status != "ACTIVE":
                row.status = "ACTIVE"
                row.deleted_at = None
                row.updated_at = now
        else:
            if row.status != "DELETED":
                row.status = "DELETED"
                row.deleted_at = now
                row.updated_at = now
    for rid in desired - existing.keys():
        db.add(UserRoleModel(user_id=user_id, role_id=rid, status="ACTIVE"))
    db.commit()


def _sync_user_companies(db, user_id: int, companies: list) -> None:
    """Upsert + soft delete de empresas: conserva filas existentes y su is_default."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    default_id = next(
        (item.id for item in companies if item.is_default),
        companies[0].id if companies else None,
    )
    existing = {
        uc.company_id: uc
        for uc in db.query(UserCompanyModel).filter(UserCompanyModel.user_id == user_id).all()
    }
    desired = {item.id for item in companies}
    for cid, row in existing.items():
        if cid in desired:
            new_default = cid == default_id
            if row.status != "ACTIVE" or not row.is_active:
                row.status = "ACTIVE"
                row.is_active = True
                row.deleted_at = None
                row.updated_at = now
            if row.is_default != new_default:
                row.is_default = new_default
                row.updated_at = now
        else:
            if row.status != "DELETED" or row.is_active:
                row.status = "DELETED"
                row.is_active = False
                row.deleted_at = now
                row.updated_at = now
    for cid in desired - existing.keys():
        db.add(UserCompanyModel(
            user_id=user_id,
            company_id=cid,
            is_default=cid == default_id,
            is_active=True,
            status="ACTIVE",
        ))
    db.commit()


@router.get("")
def list_users(user: CurrentUser, db: DbDep):
    user_repo = UserRepositoryImpl(db)
    use_case = ListUsersUseCase(user_repo)
    users = use_case.execute()
    data = [UserWithProfileRead.model_validate(u).model_dump() for u in users]
    return ApiResponseFactory.ok(data, "Usuarios obtenidos correctamente")


@router.post("")
def create_user(data: UserWithProfileCreate, user: CurrentUser, db: DbDep):
    if not data.password.strip():
        raise AppException.bad_request("La contrasena es obligatoria")
    if data.password == PASSWORD_SENTINEL:
        raise AppException.bad_request("La contrasena no puede ser el valor de relleno")

    role_ids = list(dict.fromkeys(data.role_ids))
    if role_ids:
        role_repo = RolePermissionRepositoryImpl(db)
        invalid_roles = [rid for rid in role_ids if role_repo.get(rid) is None]
        if invalid_roles:
            raise AppException.bad_request(f"Roles no encontrados: {invalid_roles}")

    user_repo = UserRepositoryImpl(db)
    use_case = CreateUserUseCase(user_repo)
    try:
        created_user = use_case.execute(
            email=data.email,
            hashed_password=hash_password(data.password),
            status=data.status,
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
        document_number=data.document_number,
    )

    if role_ids:
        _sync_user_roles(db, created_user.id, role_ids)

    if data.companies:
        company_repo = CompanyRepositoryImpl(db)
        invalid_ids = [
            cid
            for cid in dict.fromkeys(item.id for item in data.companies)
            if company_repo.get(cid) is None
        ]
        if invalid_ids:
            raise AppException.bad_request(
                f"Empresas no encontradas o inactivas: {invalid_ids}"
            )
        _sync_user_companies(db, created_user.id, data.companies)

    user_repo = UserRepositoryImpl(db)
    created_user = user_repo.get(created_user.id)
    data = UserWithProfileRead.model_validate(created_user).model_dump()
    return ApiResponseFactory.created(data, "Usuario creado correctamente")


@router.get("/{user_id}")
def get_user(user_id: int, user: CurrentUser, db: DbDep):
    user_repo = UserRepositoryImpl(db)
    use_case = GetUserUseCase(user_repo)
    target = use_case.execute(user_id)
    if not target:
        raise AppException.not_found("Usuario no encontrado")
    data = UserWithProfileRead.model_validate(target).model_dump()
    return ApiResponseFactory.ok(data, "Usuario obtenido correctamente")


@router.patch("/{user_id}")
def update_user(
    user_id: int,
    data: UserWithProfileUpdate,
    user: CurrentUser,
    db: DbDep,
):
    user_repo = UserRepositoryImpl(db)
    target = user_repo.get(user_id)
    if not target:
        raise AppException.not_found("Usuario no encontrado")

    payload = data.model_dump(exclude_unset=True)

    # --- validaciones de solo lectura antes de mutar ---
    email = payload.get("email")
    if email is not None and email != target.email:
        existing = user_repo.get_by_email(email)
        if existing and existing.id != user_id:
            raise AppException.conflict("Ya existe un usuario con ese email")

    role_ids: list[int] | None = None
    if "role_ids" in payload:
        role_ids = list(dict.fromkeys(payload["role_ids"]))
        if role_ids:
            role_repo = RolePermissionRepositoryImpl(db)
            invalid_roles = [rid for rid in role_ids if role_repo.get(rid) is None]
            if invalid_roles:
                raise AppException.bad_request(f"Roles no encontrados: {invalid_roles}")

    if "companies" in payload:
        company_repo = CompanyRepositoryImpl(db)
        invalid_ids = [
            cid
            for cid in dict.fromkeys(item.id for item in data.companies)
            if company_repo.get(cid) is None
        ]
        if invalid_ids:
            raise AppException.bad_request(
                f"Empresas no encontradas o inactivas: {invalid_ids}"
            )

    # --- user (email, status, password) ---
    user_kwargs: dict = {}
    if email is not None and email != target.email:
        user_kwargs["email"] = email
    if payload.get("status") is not None:
        user_kwargs["status"] = payload["status"]
    if payload.get("change_password"):
        new_password = payload.get("password")
        if new_password and new_password != PASSWORD_SENTINEL:
            if len(new_password) < 6:
                raise AppException.bad_request("La contrasena debe tener al menos 6 caracteres")
            user_kwargs["hashed_password"] = hash_password(new_password)

    if user_kwargs:
        UpdateUserUseCase(user_repo).execute(user_id, **user_kwargs)

    # --- profile ---
    profile_fields = ("first_name", "last_name", "phone", "age", "document_number")
    profile_payload = {k: payload[k] for k in profile_fields if k in payload}
    if profile_payload:
        profile_repo = ProfileRepositoryImpl(db)
        profile = profile_repo.get_by_user_id(user_id)
        if profile:
            from app.domain.entities import Profile as ProfileEntity
            profile_entity = ProfileEntity(
                id=profile.id, user_id=profile.user_id, first_name=profile.first_name,
                last_name=profile.last_name, phone=profile.phone, age=profile.age,
                document_number=profile.document_number,
                status=profile.status, created_at=profile.created_at, updated_at=profile.updated_at,
            )
            profile_repo.update(profile_entity, **profile_payload)

    # --- roles (upsert + soft delete) ---
    if role_ids is not None:
        _sync_user_roles(db, user_id, role_ids)

    # --- companies (upsert + soft delete) ---
    if "companies" in payload:
        _sync_user_companies(db, user_id, data.companies)

    target = user_repo.get(user_id)
    data = UserWithProfileRead.model_validate(target).model_dump()
    return ApiResponseFactory.ok(data, "Usuario actualizado correctamente")


@router.delete("/{user_id}")
def delete_user(user_id: int, user: CurrentUser, db: DbDep):
    target = UserRepositoryImpl(db).get(user_id)
    if not target:
        raise AppException.not_found("Usuario no encontrado")
    DeleteUserUseCase(UserRepositoryImpl(db)).execute(user_id)
    return ApiResponseFactory.no_content("Usuario eliminado correctamente")
