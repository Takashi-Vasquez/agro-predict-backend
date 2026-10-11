from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.company_context import CompanyContext
from app.infrastructure.config.security import decode_access_token
from app.infrastructure.database.session import get_db
from app.infrastructure.orm.security.user import User
from app.infrastructure.repositories.core.company_repository import CompanyRepositoryImpl
from app.infrastructure.repositories.security.auth_repository import AuthRepositoryImpl

bearer_scheme = HTTPBearer()

DbDep = Annotated[Session, Depends(get_db)]


def get_current_user(
    credentials: Annotated[HTTPBearer | None, Depends(bearer_scheme)],
    db: DbDep,
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticacion requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sub = decode_access_token(credentials.credentials)
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas o token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_repo = AuthRepositoryImpl(db)
    user = user_repo.get(int(sub))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    header_id = CompanyContext.get_empresa_id()
    if header_id is None:
        default_company_id = CompanyRepositoryImpl(db).get_default_company_id(user.id)
        if default_company_id is not None:
            CompanyContext.set_empresa_id(default_company_id)
    elif not user.is_admin and not CompanyRepositoryImpl(db).user_has_company(user.id, header_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta empresa",
        )

    return db.get(User, user.id)


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_empresa_id() -> int | None:
    return CompanyContext.get_empresa_id()


EmpresaDep = Annotated[int | None, Depends(get_empresa_id)]