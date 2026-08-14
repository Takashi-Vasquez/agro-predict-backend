from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.infrastructure.config.security import decode_access_token
from app.infrastructure.database.session import get_db
from app.infrastructure.orm.auth.user import User
from app.infrastructure.repositories.user_repository import UserRepositoryImpl

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
    user_repo = UserRepositoryImpl(db)
    user = user_repo.get(int(sub))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return db.get(User, user.id)


CurrentUser = Annotated[User, Depends(get_current_user)]
