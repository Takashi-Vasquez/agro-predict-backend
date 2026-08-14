"""Script CLI para crear un usuario administrador una sola vez.

Uso:
    python -m app.scripts.create_admin

Pide por terminal: email y contrasena.
Crea el usuario con is_admin=True en la base de datos.
"""

import sys
from getpass import getpass

from sqlalchemy.exc import IntegrityError

from app.infrastructure.config.settings import get_settings
from app.infrastructure.config.security import hash_password
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.repositories.user_repository import UserRepositoryImpl


def main() -> None:
    settings = get_settings()
    print(f"=== Crear Admin ===")
    print(f"Base de datos: {settings.DATABASE_URL.split('@')[-1]}\n")

    email = input("Email: ").strip()
    if not email:
        print("Error: el email es obligatorio")
        sys.exit(1)

    password = getpass("Contrasena: ")
    if len(password) < 6:
        print("Error: la contrasena debe tener al menos 6 caracteres")
        sys.exit(1)

    password_confirm = getpass("Confirmar contrasena: ")
    if password != password_confirm:
        print("Error: las contrasenas no coinciden")
        sys.exit(1)

    db = SessionLocal()
    try:
        repo = UserRepositoryImpl(db)

        existing = repo.get_by_email(email)
        if existing:
            print(f"\nError: ya existe un usuario con el email {email}")
            sys.exit(1)

        user = repo.create(
            email=email,
            hashed_password=hash_password(password),
            is_admin=True,
        )

        print(f"\nAdmin creado exitosamente:")
        print(f"  ID:    {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Admin: {user.is_admin}")
        print(f"\nYa puedes iniciar sesion con POST /api/v1/auth/login")
    except IntegrityError:
        print(f"\nError: ya existe un usuario con el email {email}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
