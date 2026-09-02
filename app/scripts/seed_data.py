"""Seed data: Crea permisos, menus y menu_permissions en la base de datos.

Ejecutar despues de levantar el proyecto:
    python -m app.scripts.seed_data

Es idempotente: puede ejecutarse multiples veces sin duplicar datos.
Para agregar nuevos menus o permisos, editar las listas PERMISOS y MENUS_DATA.
"""

from app.infrastructure.config.security import hash_password
from app.infrastructure.orm.security.user import User
from sqlalchemy import select

from app.infrastructure.database.session import _get_session_factory
from app.infrastructure.orm.security.menu import Menu
from app.infrastructure.orm.security.menu_permission import MenuPermission
from app.infrastructure.orm.security.permission import Permission


PERMISOS = [
    {"code": "CREATE", "name": "Crear"},
    {"code": "READ", "name": "Leer"},
    {"code": "UPDATE", "name": "Actualizar"},
    {"code": "DELETE", "name": "Eliminar"},
    {"code": "EXPORT", "name": "Exportar"},
]

MENUS_DATA = [
    {
        "name": "Dashboard",
        "route": "/dashboard",
        "icon": "dashboard",
        "order_index": 1,
        "menu_permissions": ["READ"],
    },
    {
        "name": "Modelo Predictivo",
        "route": "/modelo-predictivo",
        "icon": "analytics",
        "order_index": 2,
        "menu_permissions": [],
        "submenus": [
            {
                "name": "entrenamiento",
                "route": "/modelo-predictivo/entrenamiento",
                "order_index": 1,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
            {
                "name": "Gestionar Predicciones",
                "route": "/modelo-predictivo/gestion",
                "order_index": 2,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
        ],
    },
    {
        "name": "Seguridad",
        "route": "/seguridad",
        "icon": "security",
        "order_index": 99,
        "menu_permissions": [],
        "submenus": [
            {
                "name": "Roles",
                "route": "/seguridad/roles",
                "order_index": 1,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
            {
                "name": "Perfil Accesos",
                "route": "/seguridad/perfil-acceso",
                "order_index": 2,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
                        {
                "name": "Usuarios",
                "route": "/seguridad/usuarios",
                "order_index": 3,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
        ],
    },
]


def seed() -> None:
    db = _get_session_factory()()
    try:
        perm_created = 0
        perm_skipped = 0
        menu_created = 0
        menu_skipped = 0

        print("--- Seed: Permisos ---")
        for p in PERMISOS:
            existing = db.scalar(select(Permission).where(Permission.code == p["code"]))
            if existing:
                perm_skipped += 1
            else:
                db.add(Permission(code=p["code"], name=p["name"]))
                perm_created += 1
        db.commit()
        print(f"  Creados: {perm_created}, Ya existian: {perm_skipped}")

        print("\n--- Seed: Menus ---")
        for menu_data in MENUS_DATA:
            existing = db.scalar(
                select(Menu).where(
                    Menu.name == menu_data["name"],
                    Menu.parent_id.is_(None),
                )
            )
            if existing:
                parent = existing
                menu_skipped += 1
            else:
                parent = Menu(
                    name=menu_data["name"],
                    route=menu_data.get("route"),
                    icon=menu_data.get("icon"),
                    order_index=menu_data.get("order_index", 0),
                    parent_id=None,
                )
                db.add(parent)
                db.flush()
                menu_created += 1

            _create_menu_permissions(db, parent.id, menu_data.get("menu_permissions", []))

            for sub_data in menu_data.get("submenus", []):
                existing_sub = db.scalar(
                    select(Menu).where(
                        Menu.name == sub_data["name"],
                        Menu.parent_id == parent.id,
                    )
                )
                if existing_sub:
                    child = existing_sub
                    menu_skipped += 1
                else:
                    child = Menu(
                        name=sub_data["name"],
                        route=sub_data.get("route"),
                        order_index=sub_data.get("order_index", 0),
                        parent_id=parent.id,
                    )
                    db.add(child)
                    db.flush()
                    menu_created += 1

                _create_menu_permissions(db, child.id, sub_data.get("menu_permissions", []))

        _create_admin(db)

        db.commit()
        print(f"  Creados: {menu_created}, Ya existian: {menu_skipped}")
        print(f"\n--- Seed completado ---")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _create_menu_permissions(db, menu_id: int, perm_codes: list[str]) -> None:
    for code in perm_codes:
        perm = db.scalar(select(Permission).where(Permission.code == code))
        if not perm:
            continue
        existing = db.scalar(
            select(MenuPermission).where(
                MenuPermission.menu_id == menu_id,
                MenuPermission.permission_id == perm.id,
            )
        )
        if not existing:
            db.add(MenuPermission(menu_id=menu_id, permission_id=perm.id))

def _create_admin(db) -> None:
    admin_email = "admin@tesis.com"
    existing = db.scalar(select(User).where(User.email == admin_email))
    if not existing:
        db.add(User(
            email=admin_email,
            hashed_password=hash_password("admin@agro6020."),
            is_admin=True,
        ))
        db.commit()
        print(f"  Admin creado: {admin_email}")

if __name__ == "__main__":
    seed()
