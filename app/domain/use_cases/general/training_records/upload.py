from uuid import uuid4
from pathlib import Path

from app.infrastructure.orm.core.catalog import Catalog
from app.infrastructure.orm.core.catalog_detail import CatalogDetail
from app.presentation.schemas.general.training_records.upload import UploadResult
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql.elements import ColumnElement

from app.domain.repositories.general.training_record_repository import TrainingRecordRepository
from app.infrastructure.external.file_parser import parse_csv, parse_xlsx
from app.infrastructure.orm.general.training_field import TrainingField
from app.infrastructure.orm.operations.crop import Crop
from app.infrastructure.orm.operations.variety import Variety
from app.infrastructure.orm.general.campaign import Campaign
from app.infrastructure.database.session import _get_session_factory
import unicodedata

MAX_ROWS = 5000

REQUIRED_TEXT_FIELDS = [
    ("crop", "Cultivo"),
    ("variety", "Variedad"),
    ("campaign", "Campaña"),
    ("soil_type", "Tipo de suelo"),
    ("irrigation_type", "Tipo de riego"),
]

def normalized(column: ColumnElement) -> ColumnElement:
    """Normaliza una columna SQL para comparaciones case/whitespace-insensitive."""
    con_tilde = "ÁÉÍÓÚÜÑ"
    sin_tilde = "AEIOUUN"

    upper_col = func.upper(func.trim(column))
    
    return func.translate(upper_col, con_tilde, sin_tilde)


def normalize_value(value: str) -> str:
    """Normaliza un string de Python con el mismo criterio, sin tocar la base de datos."""
    value = value.strip().upper()
    value = unicodedata.normalize("NFKD", value)
    return "".join(char for char in value if not unicodedata.combining(char))


def _load_field_definitions() -> dict[str, dict]:
    db = _get_session_factory()()
    try:
        fields = db.query(TrainingField).filter(TrainingField.status != "DELETED").all()
        return {f.field_key: {
            "field_type": f.field_type,
            "min_value": f.min_value,
            "max_value": f.max_value,
            "options": f.options,
            "is_required": f.is_required,
        } for f in fields}
    finally:
        db.close()


def _load_label_to_field_key() -> dict[str, str]:
    db = _get_session_factory()()
    try:
        fields = db.query(TrainingField).filter(TrainingField.status != "DELETED").all()
        return {f.label: f.field_key for f in fields}
    finally:
        db.close()


def _validate_crop_variety(db: Session, crop_name: str, variety: str) -> tuple[int | None, str | None]:
    variety_obj = db.query(Variety).filter(
        normalized(Variety.name) == normalize_value(variety),
        Variety.status != "DELETED",
    ).first()
    if not variety_obj:
        return None, f"Variedad no encontrada: {variety}"

    crop = db.query(Crop).filter(
        normalized(Crop.name) == normalize_value(crop_name),
        Crop.variety_id == variety_obj.id,
        Crop.status != "DELETED",
    ).first()
    if not crop:
        return None, f"Relación cultivo-variedad no válida: {crop_name} - {variety}"

    return crop.id, None


def _validate_campaign(db: Session, code: str) -> tuple[str | None, str | None]:
    campaign = db.query(Campaign).filter(
        normalized(Campaign.code) == normalize_value(code),
        Campaign.status != "DELETED",
    ).first()
    if not campaign:
        return None, f"Campaña no encontrada: {code}"
    return code, None


def _validate_soil_type(db: Session, code: str) -> tuple[str | None, str | None]:
    soil_type = db.query(Catalog).filter(
        Catalog.code == 'soil_type',
        Catalog.status != "DELETED",
    ).first()
    if not soil_type:
        return None, "Catálogo 'Tipo de suelo' no configurado"

    soil_type_detail = db.query(CatalogDetail).filter(
        CatalogDetail.catalog_id == soil_type.id,
        normalized(CatalogDetail.value) == normalize_value(code),
        CatalogDetail.status != "DELETED",
    ).first()
    if not soil_type_detail:
        return None, f"Tipo de suelo no encontrada: {code}"

    return code, None


def _validate_irrigation_type(db: Session, code: str) -> tuple[str | None, str | None]:
    irrigation_type = db.query(Catalog).filter(
        Catalog.code == 'irrigation_type',
        Catalog.status != "DELETED",
    ).first()
    if not irrigation_type:
        return None, "Catálogo 'Tipo de riego' no configurado"

    irrigation_type_detail = db.query(CatalogDetail).filter(
        CatalogDetail.catalog_id == irrigation_type.id,
        normalized(CatalogDetail.value) == normalize_value(code),
        CatalogDetail.status != "DELETED",
    ).first()
    if not irrigation_type_detail:
        return None, f"Tipo de riego no encontrada: {code}"

    return code, None


def _validate_row(data: dict, field_defs: dict[str, dict]) -> str | None:
    for key, fdef in field_defs.items():
        if not fdef["is_required"]:
            continue
        val = data.get(key, "").strip()
        if not val:
            return f"Campo requerido vacío: {key}"

        if fdef["field_type"] in ("number", "integer"):
            try:
                num = float(val)
            except ValueError:
                return f"Valor no numérico en {key}: {val}"
            if fdef["min_value"] is not None and num < fdef["min_value"]:
                return f"Valor menor al mínimo en {key}: {num} < {fdef['min_value']}"
            if fdef["max_value"] is not None and num > fdef["max_value"]:
                return f"Valor mayor al máximo en {key}: {num} > {fdef['max_value']}"
        elif fdef["field_type"] == "select":
            if fdef["options"] and val not in fdef["options"]:
                return f"Opción inválida en {key}: {val}. Opciones: {', '.join(fdef['options'])}"

    return None


def _cached_validate(cache: dict, key, validate_fn):
    if key not in cache:
        value, err = validate_fn()
        cache[key] = value
        return value, err
    return cache[key], None


def process_upload(
    content: str,
    filename: str,
    user_id: int,
    record_repo: TrainingRecordRepository,
) -> UploadResult:
    field_defs = _load_field_definitions()
    label_to_field_key = _load_label_to_field_key()

    if filename.endswith(".xlsx"):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp.write(content.encode("latin-1") if isinstance(content, str) else content)
            tmp_path = Path(tmp.name)
        try:
            rows, headers = parse_xlsx(tmp_path)
        finally:
            tmp_path.unlink()
    else:
        rows, headers = parse_csv(content if isinstance(content, str) else content.decode("utf-8"))

    if not rows:
        return {"total": 0, "has_errors": True, "records": []}

    if len(rows) > MAX_ROWS:
        return {"total": len(rows), "has_errors": True, "records": [
            {"row": 1, "error": f"Máximo {MAX_ROWS} filas permitidas", **{k: "" for k in label_to_field_key.values()}}
        ]}

    db = record_repo.db
    crop_variety_cache: dict[str, int | None] = {}
    campaign_cache: dict[str, str | None] = {}
    soil_type_cache: dict[str, str | None] = {}
    irrigation_type_cache: dict[str, str | None] = {}
    records_with_error = []
    valid_records = []

    for row in rows:
        original_data = row["data"]
        row_num = row["row_number"]

        translated_data = {}
        for label, value in original_data.items():
            field_key = label_to_field_key.get(label, label)
            translated_data[field_key] = value

        values = {key: (translated_data.get(key) or "").strip() for key, _ in REQUIRED_TEXT_FIELDS}

        missing_field = next((label for key, label in REQUIRED_TEXT_FIELDS if not values[key]), None)
        if missing_field:
            records_with_error.append(
                {**translated_data, "row": row_num, "error": f"Campo requerido vacío: {missing_field}"}
            )
            continue
        crop_name = values["crop"]
        variety = values["variety"]
        campaign_code = values["campaign"]
        soil_type_val = values["soil_type"]
        irrigation_type_val = values["irrigation_type"]

        cache_key = f"{crop_name}|{variety}"
        crop_id, err = _cached_validate(crop_variety_cache, cache_key, lambda: _validate_crop_variety(db, crop_name, variety))
        if err:
            records_with_error.append({**translated_data, "row": row_num, "error": err})
            continue
        if crop_id is None:
            records_with_error.append({**translated_data, "row": row_num, "error": f"Relación cultivo-variedad no válida: {crop_name} - {variety}"})
            continue

        campaign_valid, err = _cached_validate(campaign_cache, campaign_code, lambda: _validate_campaign(db, campaign_code))
        if err:
            records_with_error.append({**translated_data, "row": row_num, "error": err})
            continue
        if campaign_valid is None:
            records_with_error.append({**translated_data, "row": row_num, "error": f"Campaña no encontrada: {campaign_code}"})
            continue

        soil_type_valid, err = _cached_validate(soil_type_cache, soil_type_val, lambda: _validate_soil_type(db, soil_type_val))
        if err:
            records_with_error.append({**translated_data, "row": row_num, "error": err})
            continue
        if soil_type_valid is None:
            records_with_error.append({**translated_data, "row": row_num, "error": f"Tipo de suelo no encontrada: {soil_type_val}"})
            continue

        irrigation_type_valid, err = _cached_validate(irrigation_type_cache, irrigation_type_val, lambda: _validate_irrigation_type(db, irrigation_type_val))
        if err:
            records_with_error.append({**translated_data, "row": row_num, "error": err})
            continue
        if irrigation_type_valid is None:
            records_with_error.append({**translated_data, "row": row_num, "error": f"Tipo de riego no encontrada: {irrigation_type_val}"})
            continue

        field_error = _validate_row(translated_data, field_defs)
        if field_error:
            records_with_error.append({**translated_data, "row": row_num, "error": field_error})
            continue

        valid_records.append({
            "row": row_num,
            "user_id": user_id,
            "crop_id": crop_id,
            "crop": translated_data.get("crop", None) or None,
            "campaign": campaign_code,
            "location": translated_data.get("location", None) or None,
            "nitrogen": float(translated_data.get("nitrogen", 0)),
            "phosphorus": float(translated_data.get("phosphorus", 0)),
            "potassium": float(translated_data.get("potassium", 0)),
            "temperature": float(translated_data.get("temperature", 0)),
            "humidity": float(translated_data.get("humidity", 0)),
            "ph_soil": float(translated_data.get("ph_soil", 0)),
            "rainfall": float(translated_data.get("rainfall", 0)),
            "irrigation_type": translated_data.get("irrigation_type", None) or None,
            "variety": variety,
            "soil_type": translated_data.get("soil_type", None) or None,
            "target_yield": float(translated_data.get("target_yield", 0)),
            "error": "",
            "source": "excel" if filename.endswith(".xlsx") else "csv",
            "import_batch_id": uuid4(),
            "status": "ACTIVE",
        })

    if records_with_error:
        all_records = [*records_with_error, *valid_records]
        return UploadResult(
          total= len(rows),
          has_errors= True,
          records= sorted(all_records, key=lambda r: r["row"])[:50],
        )

    batch_id = uuid4()
    for r in valid_records:
        r["import_batch_id"] = batch_id

    record_repo.create_batch(valid_records)

    return UploadResult(
      total= len(rows),
      has_errors= False,
      batch_id= str(batch_id),
      saved= len(valid_records),
    )