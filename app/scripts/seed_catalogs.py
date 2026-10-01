"""Seed de catálogos maestros: soil_type, irrigation_type, variety."""

from app.infrastructure.database.session import _get_session_factory
from app.infrastructure.orm.core.catalog import Catalog
from app.infrastructure.orm.core.catalog_detail import CatalogDetail

CATALOGS_DATA = [
    {
        "code": "soil_type",
        "label": "Tipo de suelo",
        "description": "Clasificación textural del suelo para cultivos",
        "details": [
            {"value": "arcilloso", "label": "Arcilloso", "order_index": 1},
            {"value": "arenoso", "label": "Arenoso", "order_index": 2},
            {"value": "limoso", "label": "Limoso", "order_index": 3},
            {"value": "franco", "label": "Franco", "order_index": 4},
            {"value": "franco_arcilloso", "label": "Franco arcilloso", "order_index": 5},
            {"value": "franco_limoso", "label": "Franco limoso", "order_index": 6},
        ],
    },
    {
        "code": "irrigation_type",
        "label": "Tipo de riego",
        "description": "Método de riego utilizado en el cultivo",
        "details": [
            {"value": "goteo", "label": "Goteo", "order_index": 1},
            {"value": "aspersion", "label": "Aspersión", "order_index": 2},
            {"value": "gravedad", "label": "Gravedad", "order_index": 3},
            {"value": "sin_riego", "label": "Sin riego", "order_index": 4},
        ],
    },
    {
        "code": "variety",
        "label": "Variedad",
        "description": "Variedad de cultivo",
        "details": [
            {"value": "hass", "label": "Hass", "order_index": 1},
            {"value": "fuerte", "label": "Fuerte", "order_index": 2},
            {"value": "zutano", "label": "Zutano", "order_index": 3},
            {"value": "hass_816", "label": "Hass 816", "order_index": 4},
            {"value": "lula", "label": "Lula", "order_index": 5},
            {"value": "edaderezo", "label": "Eda Derezo", "order_index": 6},
        ],
    },
    {
        "code": "campaign_status",
        "label": "Estado de campaña",
        "description": "Estados posibles para una campaña de cultivo",
        "details": [
            {"value": "PLANNED", "label": "Planificado", "order_index": 1},
            {"value": "ACTIVE", "label": "Activo", "order_index": 2},
            {"value": "PAUSED", "label": "Pausado", "order_index": 3},
            {"value": "CLOSED", "label": "Cerrado", "order_index": 4},
        ],
    },
    {
        "code": "record_status",
        "label": "Estado de registro",
        "description": "Estados de bitácora: activo, inactivo, eliminado",
        "details": [
            {"value": "ACTIVE", "label": "Activo", "order_index": 1},
            {"value": "INACTIVE", "label": "Inactivo", "order_index": 2},
            {"value": "DELETED", "label": "Eliminado", "order_index": 3},
        ],
    },
]


def seed_catalogs() -> None:
    db = _get_session_factory()()
    try:
        catalogs_created = 0
        catalogs_skipped = 0
        details_created = 0
        details_skipped = 0

        for cat_data in CATALOGS_DATA:
            existing = db.query(Catalog).filter(Catalog.code == cat_data["code"]).first()
            if existing:
                catalogs_skipped += 1
                catalog = existing
            else:
                catalog = Catalog(
                    code=cat_data["code"],
                    label=cat_data["label"],
                    description=cat_data.get("description"),
                    is_active=True,
                    status="ACTIVE",
                )
                db.add(catalog)
                db.flush()
                catalogs_created += 1

            for det_data in cat_data["details"]:
                det_existing = (
                    db.query(CatalogDetail)
                    .filter(
                        CatalogDetail.catalog_id == catalog.id,
                        CatalogDetail.value == det_data["value"],
                    )
                    .first()
                )
                if det_existing:
                    details_skipped += 1
                else:
                    detail = CatalogDetail(
                        catalog_id=catalog.id,
                        value=det_data["value"],
                        label=det_data["label"],
                        order_index=det_data["order_index"],
                        is_active=True,
                        status="ACTIVE",
                    )
                    db.add(detail)
                    details_created += 1

        db.commit()
        print(f"  Catálogos creados: {catalogs_created}, Ya existían: {catalogs_skipped}")
        print(f"  Detalles creados: {details_created}, Ya existían: {details_skipped}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("--- Seed: Catálogos ---")
    seed_catalogs()
    print("--- Seed Catálogos completado ---")
