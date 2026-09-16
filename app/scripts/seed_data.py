"""Seed data: Crea permisos, menus y menu_permissions en la base de datos.

Ejecutar despues de levantar el proyecto:
    python -m app.scripts.seed_data

Es idempotente: puede ejecutarse multiples veces sin duplicar datos.
Para agregar nuevos menus o permisos, editar las listas PERMISOS y MENUS_DATA.
"""

from datetime import datetime

from sqlalchemy import select

from app.infrastructure.config.security import hash_password
from app.infrastructure.database.session import _get_session_factory
from app.infrastructure.orm.operations.crop import Crop
from app.infrastructure.orm.security.menu import Menu
from app.infrastructure.orm.security.menu_permission import MenuPermission
from app.infrastructure.orm.security.permission import Permission
from app.infrastructure.orm.security.role_menu_permission import RoleMenuPermission
from app.infrastructure.orm.security.user import User


PERMISOS = [
    {"code": "CREATE", "name": "Crear"},
    {"code": "READ", "name": "Leer"},
    {"code": "UPDATE", "name": "Actualizar"},
    {"code": "DELETE", "name": "Eliminar"},
    {"code": "EXPORT", "name": "Exportar"},
]

MENUS_DATA = [
    {
        "code": "GENERAL_PANEL",
        "name": "Panel General",
        "route": "/panel-general",
        "icon": "",
        "order_index": 1,
        "badge": None,
        "menu_permissions": [],
        "submenus": [
            {
                "code": "GENERAL_PANEL.DASHBOARD",
                "name": "Dashboard",
                "route": "/panel-general/dashboard",
                "icon": "grid",
                "order_index": 1,
                "badge": None,
                "menu_permissions": ["READ"],
            },
            {
                "code": "GENERAL_PANEL.PREDICTIONS",
                "name": "Predicciones",
                "route": "/panel-general/predicciones",
                "icon": "sparkles",
                "order_index": 2,
                "badge": "IA",
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
        ],
    },
    {
        "code": "OPERATION",
        "name": "Operaciones",
        "route": "/operaciones",
        "icon": "",
        "order_index": 2,
        "badge": None,
        "menu_permissions": [],
        "submenus": [
            {
                "code": "OPERATION.CROPS",
                "name": "Cultivos",
                "route": "/operaciones/cultivos",
                "icon": "sprout",
                "order_index": 1,
                "badge": None,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
            {
                "code": "OPERATION.PLANNING",
                "name": "Planificación",
                "route": "/operaciones/planificacion",
                "icon": "calendar",
                "order_index": 2,
                "badge": None,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
            {
                "code": "OPERATION.PLOTS",
                "name": "Parcelas",
                "route": "/operaciones/parcelas",
                "icon": "layers",
                "order_index": 3,
                "badge": None,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            }
        ],
    },
    {
        "code": "MONITORING",
        "name": "Monitoreo",
        "route": "/monitoreo",
        "icon": "",
        "order_index": 3,
        "badge": None,
        "menu_permissions": [],
        "submenus": [
            {
                "code": "MONITORING.WEATHER",
                "name": "Clima",
                "route": "/monitoreo/clima",
                "icon": "sun",
                "order_index": 1,
                "badge": None,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
            {
                "code": "MONITORING.SENSORS",
                "name": "Sensores IoT",
                "route": "/monitoreo/sensores",
                "icon": "sensor",
                "order_index": 2,
                "badge": None,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
            {
                "code": "MONITORING.HISTORY",
                "name": "Historial",
                "route": "/monitoreo/historial",
                "icon": "history",
                "order_index": 3,
                "badge": None,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
            {
                "code": "MONITORING.REPORTS",
                "name": "Reportes",
                "route": "/monitoreo/reportes",
                "icon": "chart",
                "order_index": 4,
                "badge": None,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            }
        ],
    },
    {
        "code": "SECURITY",
        "name": "Seguridad",
        "route": "/seguridad",
        "icon": "security",
        "order_index": 99,
        "badge": None,
        "menu_permissions": [],
        "submenus": [
            {
                "code": "SECURITY.ROLES",
                "name": "Roles",
                "route": "/seguridad/roles",
                "icon": "user",
                "order_index": 1,
                "badge": None,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
            {
                "code": "SECURITY.ACCESS_PROFILE",
                "name": "Perfil Accesos",
                "route": "/seguridad/perfil-acceso",
                "icon": "shield",
                "order_index": 2,
                "badge": None,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
            {
                "code": "SECURITY.USER",
                "name": "Usuarios",
                "route": "/seguridad/usuarios",
                "icon": "user",
                "order_index": 3,
                "badge": None,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
            {
                "code": "SECURITY.SETTINGS",
                "name": "Configuracion",
                "route": "/seguridad/configuracion",
                "icon": "settings",
                "order_index": 4,
                "badge": None,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
            {
                "code": "SECURITY.PROFILE",
                "name": "Perfil",
                "route": "/seguridad/perfil",
                "icon": "user",
                "order_index": 5,
                "badge": None,
                "menu_permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            },
        ],
    },
]


def _normalize_code(code: str) -> str:
    return code.strip().upper()


def _collect_menu_codes(menu_items: list[dict]) -> set[str]:
    codes: set[str] = set()
    for item in menu_items:
        codes.add(_normalize_code(item["code"]))
        codes.update(_collect_menu_codes(item.get("submenus", [])))
    return codes


def _validate_menu_permissions(menu_data: dict, perm_codes_normalized: set[str]) -> list[str]:
    normalized = []
    for raw_code in menu_data.get("menu_permissions", []):
        code = _normalize_code(raw_code)
        if code not in perm_codes_normalized:
            raise ValueError(
                f"menu_permissions code '{raw_code}' not found in PERMISOS. "
                f"Available: {sorted(perm_codes_normalized)}"
            )
        normalized.append(code)
    return normalized


def _validate_all_permissions(menu_items: list[dict], perm_codes_normalized: set[str]) -> None:
    for item in menu_items:
        _validate_menu_permissions(item, perm_codes_normalized)
        for sub in item.get("submenus", []):
            _validate_all_permissions([sub], perm_codes_normalized)


def seed() -> None:
    db = _get_session_factory()()
    now = datetime.utcnow()
    try:
        perm_created = 0
        perm_skipped = 0
        menu_created = 0
        menu_skipped = 0
        menu_reactivated = 0
        menu_deactivated = 0

        print("--- Seed: Permisos ---")
        for p in PERMISOS:
            code = _normalize_code(p["code"])
            existing = db.scalar(select(Permission).where(Permission.code == code))
            if existing:
                perm_skipped += 1
            else:
                db.add(Permission(code=code, name=p["name"]))
                perm_created += 1
        db.commit()
        print(f"  Creados: {perm_created}, Ya existian: {perm_skipped}")

        perm_codes_normalized = {_normalize_code(p["code"]) for p in PERMISOS}

        print("\n--- Validando MENUS_DATA ---")
        _validate_all_permissions(MENUS_DATA, perm_codes_normalized)
        print("  Todos los permisos en MENUS_DATA son validos")

        code_menu_codes = _collect_menu_codes(MENUS_DATA)

        print("\n--- Sync: Menus ---")
        menu_deactivated, menu_reactivated = _sync_menus(db, code_menu_codes, now)
        print(f"  Desactivados: {menu_deactivated}, Reactivados: {menu_reactivated}")

        print("\n--- Seed: Menus ---")
        for menu_data in MENUS_DATA:
            menu_created, menu_skipped = _seed_menu_tree(db, menu_data, None, menu_created, menu_skipped, now)

        _create_admin(db)
        _create_crops(db)

        db.commit()
        print(f"  Creados: {menu_created}, Ya existian: {menu_skipped}")
        print(f"\n--- Seed completado ---")

        _drift_detection(db, code_menu_codes)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _sync_menus(db, code_menu_codes: set[str], now: datetime) -> tuple[int, int]:
    deactivated = 0
    reactivated = 0

    all_menus = db.scalars(select(Menu)).all()

    for menu in all_menus:
        if not menu.code:
            continue

        menu_code = _normalize_code(menu.code)

        if menu.status != "DELETED" and menu_code not in code_menu_codes:
            menu.status = "DELETED"
            menu.deleted_at = now
            deactivated += 1

            db.scalars(
                select(MenuPermission).where(MenuPermission.menu_id == menu.id)
            )
            for mp in db.scalars(select(MenuPermission).where(MenuPermission.menu_id == menu.id)).all():
                if mp.status != "DELETED":
                    mp.status = "DELETED"
                    mp.deleted_at = now

            for rmp in db.scalars(
                select(RoleMenuPermission).where(RoleMenuPermission.menu_id == menu.id)
            ).all():
                if rmp.status != "DELETED":
                    rmp.status = "DELETED"
                    rmp.deleted_at = now

        elif menu.status == "DELETED" and menu_code in code_menu_codes:
            menu.status = "ACTIVE"
            menu.updated_at = now
            reactivated += 1

            for mp in db.scalars(select(MenuPermission).where(MenuPermission.menu_id == menu.id)).all():
                if mp.status == "DELETED":
                    mp.status = "ACTIVE"
                    mp.updated_at = now

            for rmp in db.scalars(select(RoleMenuPermission).where(RoleMenuPermission.menu_id == menu.id)).all():
                if rmp.status == "DELETED":
                    rmp.status = "ACTIVE"
                    rmp.updated_at = now

    return deactivated, reactivated


def _seed_menu_tree(
    db,
    menu_data: dict,
    parent_id: int | None,
    created: int,
    skipped: int,
    now: datetime,
) -> tuple[int, int]:
    code = _normalize_code(menu_data["code"])
    existing = db.scalar(
        select(Menu).where(Menu.code == code, Menu.parent_id == parent_id)
    )
    if existing:
        menu = existing
        if menu.status == "DELETED":
            menu.status = "ACTIVE"
        menu.name = menu_data["name"]
        menu.route = menu_data.get("route")
        menu.icon = menu_data.get("icon")
        menu.order_index = menu_data.get("order_index", 0)
        menu.badge = menu_data.get("badge")
        menu.updated_at = now
        skipped += 1
    else:
        menu = Menu(
            code=code,
            name=menu_data["name"],
            route=menu_data.get("route"),
            icon=menu_data.get("icon"),
            order_index=menu_data.get("order_index", 0),
            badge=menu_data.get("badge"),
            parent_id=parent_id,
        )
        db.add(menu)
        db.flush()
        created += 1

    for raw_code in menu_data.get("menu_permissions", []):
        perm_code = _normalize_code(raw_code)
        perm = db.scalar(select(Permission).where(Permission.code == perm_code))
        if not perm:
            continue
        existing_mp = db.scalar(
            select(MenuPermission).where(
                MenuPermission.menu_id == menu.id,
                MenuPermission.permission_id == perm.id,
            )
        )
        if not existing_mp:
            db.add(MenuPermission(menu_id=menu.id, permission_id=perm.id))
        elif existing_mp.status == "DELETED":
            existing_mp.status = "ACTIVE"
            existing_mp.updated_at = now

    for sub_data in menu_data.get("submenus", []):
        created, skipped = _seed_menu_tree(db, sub_data, menu.id, created, skipped, now)

    return created, skipped

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

CROPS_DATA = [
    {
        "name": "Palta",
        "variety": "Hass",
        "category": "Frutal",
        "cycle": 330,
        "temperature": "17–25 °C",
        "water": "Riego tecnificado",
        "color": "#a6b96f",
    },
    {
        "name": "Arándano",
        "variety": "Biloxi",
        "category": "Frutal",
        "cycle": 240,
        "temperature": "16–24 °C",
        "water": "Riego tecnificado",
        "color": "#36734f",
    },
]

def _create_crops(db) -> None:
    admin_email = "admin@tesis.com"
    admin = db.scalar(select(User).where(User.email == admin_email))
    if not admin:
        print("  Saltando crops: no hay admin")
        return

    crops_created = 0
    crops_skipped = 0
    for c in CROPS_DATA:
        existing = db.scalar(select(Crop).where(Crop.name == c["name"], Crop.owner_id == admin.id))
        if existing:
            crops_skipped += 1
        else:
            db.add(Crop(
                owner_id=admin.id,
                name=c["name"],
                variety=c["variety"],
                category=c["category"],
                cycle=c["cycle"],
                temperature=c["temperature"],
                water=c["water"],
                color=c["color"],
            ))
            crops_created += 1
    db.commit()
    print(f"  Crops creados: {crops_created}, Ya existían: {crops_skipped}")

def _drift_detection(db, code_menu_codes: set[str]) -> None:
    print("\n--- Drift Detection ---")

    perm_codes_normalized = {_normalize_code(p["code"]) for p in PERMISOS}
    db_perm_codes = {_normalize_code(p.code) for p in db.scalars(select(Permission)).all()}
    in_bd_not_code = db_perm_codes - perm_codes_normalized
    in_code_not_bd = perm_codes_normalized - db_perm_codes

    if in_bd_not_code:
        print(f"  Permisos en BD pero no en PERMISOS: {sorted(in_bd_not_code)}")
    if in_code_not_bd:
        print(f"  Permisos en PERMISOS pero no en BD: {sorted(in_code_not_bd)}")
    if not in_bd_not_code and not in_code_not_bd:
        print("  Permisos: OK (sin drift)")

    db_menu_codes = {_normalize_code(m.code) for m in db.scalars(select(Menu)).all() if m.code}

    in_bd_not_menu = db_menu_codes - code_menu_codes
    in_menu_not_bd = code_menu_codes - db_menu_codes

    if in_bd_not_menu:
        print(f"  Menus en BD pero no en MENUS_DATA: {sorted(in_bd_not_menu)}")
    if in_menu_not_bd:
        print(f"  Menus en MENUS_DATA pero no en BD: {sorted(in_menu_not_bd)}")
    if not in_bd_not_menu and not in_menu_not_bd:
        print("  Menus: OK (sin drift)")


if __name__ == "__main__":
    seed()
