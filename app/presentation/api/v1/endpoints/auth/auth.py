from fastapi import APIRouter

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.schemas.security.auth.token import LoginRequest, Token
from app.presentation.schemas.security.users.user_me import UserMeRead, MenuTreeRead, CompanyMeRead, RoleBriefRead
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.repositories.security.auth_repository import AuthRepositoryImpl
from app.infrastructure.repositories.security.menu_repository import MenuRepositoryImpl
from app.infrastructure.repositories.security.role_permission_repository import RolePermissionRepositoryImpl
from app.infrastructure.repositories.core.company_repository import CompanyRepositoryImpl
from app.domain.exceptions import AppException
from app.domain.use_cases.auth.login import LoginUseCase
from app.domain.use_cases.auth.get_user import GetUserUseCase

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: DbDep) -> Token:
    auth_repo = AuthRepositoryImpl(db)
    use_case = LoginUseCase(auth_repo)
    try:
        _user, token = use_case.execute(data.email, data.password)
    except ValueError as exc:
        raise AppException.unauthorized(str(exc))
    return ApiResponseFactory.ok(Token(accessToken=token).model_dump(), "Login exitoso")


@router.get("/user")
def get_user(user: CurrentUser, db: DbDep):
    use_case = GetUserUseCase(
        auth_repo=AuthRepositoryImpl(db),
        menu_repo=MenuRepositoryImpl(db),
        company_repo=CompanyRepositoryImpl(db),
        role_permission_repo=RolePermissionRepositoryImpl(db),
    )
    result = use_case.execute(user.id)

    profile = result["profile"]
    companies = [
        CompanyMeRead(
            id=company.id,
            code=company.code,
            name=company.name,
            ruc=company.ruc,
            logo_path=company.logo_path,
            is_default=is_default,
        )
        for company, is_default in result["companies"]
    ]

    data = UserMeRead(
        id=result["user"].id,
        email=result["user"].email,
        status=result["user"].status,
        is_admin=result["user"].is_admin,
        first_name=profile.first_name if profile else None,
        last_name=profile.last_name if profile else None,
        full_name=f"{profile.first_name} {profile.last_name}".strip() if profile else None,
        phone=profile.phone if profile else None,
        age=profile.age if profile else None,
        roles=[RoleBriefRead(id=r["id"], name=r["name"]) for r in result["roles"]],
        companies=companies,
        menus=[MenuTreeRead(**m) for m in result["menus"]],
    )
    return ApiResponseFactory.ok(data.model_dump(), "Usuario obtenido correctamente")
