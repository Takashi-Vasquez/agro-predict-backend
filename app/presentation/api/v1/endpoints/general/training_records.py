from app.presentation.schemas.common import ApiResponse
from fastapi import APIRouter, File, Query, UploadFile

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.repositories.general.training_record_repository import TrainingRecordRepositoryImpl
from app.infrastructure.repositories.operations.crop_repository import CropRepositoryImpl
from app.presentation.schemas.general.training_records.training_record import (
    TrainingRecordCreate,
    TrainingRecordRead,
    TrainingRecordStats,
)
from app.presentation.schemas.general.training_records.upload import (
    UploadResult,
)
from app.domain.exceptions import AppException
from app.domain.use_cases.general.training_records.create import CreateTrainingRecordUseCase
from app.domain.use_cases.general.training_records.list_records import ListTrainingRecordsUseCase
from app.domain.use_cases.general.training_records.get_record import GetTrainingRecordUseCase
from app.domain.use_cases.general.training_records.delete import DeleteTrainingRecordUseCase
from app.domain.use_cases.general.training_records.stats import GetTrainingStatsUseCase
from app.domain.use_cases.general.training_records.upload import process_upload
from app.domain.use_cases.general.training_records.template import generate_template
from app.infrastructure.repositories.general.training_field_repository import TrainingFieldRepositoryImpl
from app.domain.use_cases.general.training_records.list_training_fields import ListTrainingFieldsUseCase
from app.presentation.schemas.general.training_records.training_field import TrainingFieldRead


router = APIRouter(prefix="/general/training-records", tags=["General/Training Records"])


@router.get("/stats")
def get_stats(user: CurrentUser, db: DbDep):
    use_case = GetTrainingStatsUseCase(TrainingRecordRepositoryImpl(db))
    raw = use_case.execute()
    data = TrainingRecordStats.model_validate(raw).model_dump(by_alias=True)
    return ApiResponseFactory.ok(data, "Estadísticas obtenidas correctamente")


@router.get("/template")
def download_template(format: str = Query("xlsx", pattern="^(xlsx|csv)$")):
    content, filename, content_type = generate_template(format=format)
    from fastapi.responses import Response
    return Response(content=content, media_type=content_type, headers={
        "Content-Disposition": f'attachment; filename="{filename}"'
    })


@router.post("/upload", response_model=ApiResponse[UploadResult])
async def upload_file(
    file: UploadFile = File(...),
    user: CurrentUser = None,
    db: DbDep = None,
):
    if not file.filename:
        raise AppException.bad_request("Archivo no válido")

    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if ext not in ("csv", "xlsx"):
        raise AppException.bad_request("Formato no soportado. Usa CSV o XLSX")

    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise AppException.bad_request("Archivo muy grande. Máximo 25MB")

    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        text_content = content.decode("latin-1")

    repo = TrainingRecordRepositoryImpl(db)
    result = process_upload(
        content=text_content,
        filename=file.filename,
        user_id=user.id,
        record_repo=repo,
    )

    if result.has_errors:
        return ApiResponseFactory.ok(result, f"Se encontraron errores de validación en {len(result.records)} fila(s)")

    return ApiResponseFactory.ok(result, "Archivo procesado correctamente")

@router.get("/fields")
def list_training_fields(user: CurrentUser, db: DbDep):
    repo = TrainingFieldRepositoryImpl(db)
    use_case = ListTrainingFieldsUseCase(repo)
    fields = use_case.execute()
    data = [TrainingFieldRead.model_validate(f).model_dump(by_alias=True) for f in fields]
    return ApiResponseFactory.ok(data, "Training fields obtenidos correctamente")

@router.get("")
def list_records(
    user: CurrentUser,
    db: DbDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    crop_id: int | None = Query(None, description="Filtrar por cultivo"),
):
    use_case = ListTrainingRecordsUseCase(TrainingRecordRepositoryImpl(db))
    rows = use_case.execute(offset=offset, limit=limit, crop_id=crop_id)
    data = [TrainingRecordRead.model_validate(r).model_dump() for r in rows]
    return ApiResponseFactory.ok(data, "Registros obtenidos correctamente")


@router.get("/{record_id}")
def get_record(record_id: int, user: CurrentUser, db: DbDep):
    use_case = GetTrainingRecordUseCase(TrainingRecordRepositoryImpl(db))
    record = use_case.execute(record_id)
    if record is None:
        raise AppException.not_found("Registro no encontrado")
    data = TrainingRecordRead.model_validate(record).model_dump()
    return ApiResponseFactory.ok(data, "Registro obtenido correctamente")


@router.post("")
def create_record(payload: TrainingRecordCreate, user: CurrentUser, db: DbDep):
    crop = CropRepositoryImpl(db).get(payload.crop_id)
    if not crop:
        raise AppException.not_found("Cultivo no encontrado")
    payload.variety = crop.variety

    use_case = CreateTrainingRecordUseCase(TrainingRecordRepositoryImpl(db))
    record = use_case.execute(user.id, payload.model_dump())
    data = TrainingRecordRead.model_validate(record).model_dump()
    return ApiResponseFactory.created(data, "Registro creado correctamente")


@router.delete("/{record_id}")
def delete_record(record_id: int, user: CurrentUser, db: DbDep):
    use_case = DeleteTrainingRecordUseCase(TrainingRecordRepositoryImpl(db))
    try:
        use_case.execute(record_id)
    except ValueError as exc:
        raise AppException.not_found(str(exc))
    return ApiResponseFactory.no_content("Registro eliminado correctamente")
