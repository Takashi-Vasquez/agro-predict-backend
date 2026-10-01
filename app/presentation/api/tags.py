from typing import Any


TAGS: list[dict[str, Any]] = [
    {"name": "Auth", "description": "Autenticacion y sesiones"},
    {"name": "Security/Users", "description": "Gestion de usuarios"},
    {"name": "Security/Roles", "description": "Gestion de roles"},
    {"name": "Security/Permissions", "description": "Menus, permisos y asignaciones"},
    {"name": "Operations/Crops", "description": "CRUD de cultivos"},
    {"name": "Operations/Varieties", "description": "Listado de variedades (solo lectura)"},
    {"name": "Operations/Predictions", "description": "Predicciones de cultivos"},
    {"name": "Monitoring/Weather", "description": "Clima, pronostico y alertas meteorologicas"},
    {"name": "General/Training Records", "description": "Registros de datos historicos para entrenamiento"},
    {"name": "General/Trained Models", "description": "Modelos ML entrenados, seleccion y metricas"},
    {"name": "General/Campaigns", "description": "Campanas de cultivo, planificacion y seguimiento"},
    {"name": "Core/Catalogs", "description": "Catalogos maestros (tipos de suelo, riego, variedades, etc.)"},
    {"name": "Core/Select Options", "description": "Opciones genericas para selects del frontend"},
]


def get_tags() -> list[dict[str, Any]]:
    return TAGS
