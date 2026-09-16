from typing import Any


TAGS: list[dict[str, Any]] = [
    {"name": "Auth", "description": "Autenticacion y sesiones"},
    {"name": "Security/Users", "description": "Gestion de usuarios"},
    {"name": "Security/Roles", "description": "Gestion de roles"},
    {"name": "Security/Permissions", "description": "Menus, permisos y asignaciones"},
    {"name": "Operations/Crops", "description": "CRUD de cultivos"},
    {"name": "Operations/Predictions", "description": "Predicciones de cultivos"},
]


def get_tags() -> list[dict[str, Any]]:
    return TAGS
