from fastapi import APIRouter

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.schemas.auth.token import LoginRequest, Token
from app.presentation.schemas.auth.user_me import UserMeRead, MenuTreeRead, RoleRead
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.repositories.user_repository import UserRepositoryImpl
from app.infrastructure.repositories.profile_repository import ProfileRepositoryImpl
from app.infrastructure.repositories.user_role_repository import UserRoleRepositoryImpl
from app.infrastructure.repositories.menu_repository import MenuRepositoryImpl
from app.domain.exceptions import AppException
from app.domain.use_cases.auth.login import LoginUseCase
from app.domain.use_cases.auth.get_user import GetUserUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: DbDep) -> Token:
    user_repo = UserRepositoryImpl(db)
    use_case = LoginUseCase(user_repo)
    try:
        _user, token = use_case.execute(data.email, data.password)
    except ValueError as exc:
        raise AppException.unauthorized(str(exc))
    return ApiResponseFactory.ok(Token(access_token=token).model_dump(), "Login exitoso")


@router.get("/user")
def get_user(user: CurrentUser, db: DbDep):
    use_case = GetUserUseCase(
        user_repo=UserRepositoryImpl(db),
        profile_repo=ProfileRepositoryImpl(db),
        user_role_repo=UserRoleRepositoryImpl(db),
        menu_repo=MenuRepositoryImpl(db),
    )
    result = use_case.execute(user.id)

    profile = result["profile"]

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
        roles=[RoleRead.model_validate(ur.role) for ur in result["roles"]],
        menus=[MenuTreeRead(**m) for m in result["menus"]],
    )
    return ApiResponseFactory.ok(data.model_dump(), "Usuario obtenido correctamente")
