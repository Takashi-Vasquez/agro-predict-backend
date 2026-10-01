from fastapi import APIRouter, Query, Body
from sqlalchemy import text

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.repositories.general.trained_model_repository import TrainedModelRepositoryImpl
from app.infrastructure.repositories.general.training_record_repository import TrainingRecordRepositoryImpl
from app.infrastructure.repositories.general.model_version_repository import ModelVersionRepositoryImpl
from app.infrastructure.repositories.general.model_run_repository import ModelRunRepositoryImpl
from app.infrastructure.config.settings import get_settings
from app.infrastructure.ml.training_jobs import submit_training_job, get_job_status
from app.presentation.schemas.general.trained_models.trained_model import (
    TrainRequest,
    TrainResponse,
    TrainedModelRead,
    TrainedModelDetail,
    SelectModelResponse,
    ModelVersionRead,
    ModelRunRead,
    PromoteRequest,
    RollbackRequest,
)
from app.domain.use_cases.general.trained_models.train import TrainModelsUseCase
from app.domain.use_cases.general.trained_models.list_models import ListModelsUseCase
from app.domain.use_cases.general.trained_models.get_model import GetModelUseCase
from app.domain.use_cases.general.trained_models.select_model import SelectModelUseCase
from app.domain.use_cases.general.trained_models.promote import PromoteModelUseCase
from app.domain.use_cases.general.trained_models.rollback import RollbackModelUseCase
from app.domain.use_cases.general.trained_models.model_version import (
    GetModelVersionUseCase,
    ListModelVersionsUseCase,
    GetProductionModelUseCase,
)
from app.domain.use_cases.general.trained_models.model_run import ListModelRunsUseCase
from app.domain.exceptions import AppException
from app.infrastructure.ml.training_jobs import submit_training_job, get_job_status
from app.infrastructure.ml.model_registry import get_registry

router = APIRouter(prefix="/general/trained-models", tags=["General/Trained Models"])


@router.post("/train")
def train_models_endpoint(
    payload: TrainRequest,
    user: CurrentUser,
    db: DbDep,
):
    settings = get_settings()
    record_repo = TrainingRecordRepositoryImpl(db)
    model_repo = TrainedModelRepositoryImpl(db)
    use_case = TrainModelsUseCase(record_repo, model_repo, settings.ML_MODEL_PATH.parent, payload.bump_level, db)

    try:
        raw = use_case.execute(payload.algorithms)
    except ValueError as exc:
        raise AppException.bad_request(str(exc))

    data = TrainResponse(**raw).model_dump(by_alias=True)
    return ApiResponseFactory.ok(data, "Entrenamiento completado")


@router.post("/train-async")
def train_models_async(
    payload: TrainRequest,
    user: CurrentUser,
    db: DbDep,
):
    settings = get_settings()
    job_id = submit_training_job(
        user_id=user.id,
        algorithms=payload.algorithms,
        record_repo_factory=None,
        model_repo_factory=None,
        artifacts_dir=settings.ML_MODEL_PATH.parent,
        bump_level=payload.bump_level,
    )
    return ApiResponseFactory.ok({"jobId": job_id}, "Entrenamiento iniciado")


@router.get("/jobs/{job_id}")
def get_training_job(job_id: str, user: CurrentUser):
    job = get_job_status(job_id, user.id)
    if job is None:
        raise AppException.not_found("Job no encontrado")
    return ApiResponseFactory.ok(job, "Estado del job")


@router.get("")
def list_models(user: CurrentUser, db: DbDep):
    model_repo = TrainedModelRepositoryImpl(db)
    use_case = ListModelsUseCase(model_repo)
    raw_list = use_case.execute()
    data = [TrainedModelRead(**m).model_dump(by_alias=True) for m in raw_list]
    return ApiResponseFactory.ok(data, "Modelos obtenidos correctamente")


@router.get("/{model_id}")
def get_model(model_id: int, user: CurrentUser, db: DbDep):
    model_repo = TrainedModelRepositoryImpl(db)
    use_case = GetModelUseCase(model_repo)
    raw = use_case.execute(model_id)
    if raw is None:
        raise AppException.not_found("Modelo no encontrado")
    data = TrainedModelDetail(**raw).model_dump(by_alias=True)
    return ApiResponseFactory.ok(data, "Modelo obtenido correctamente")


@router.patch("/{model_id}/select")
def select_model(model_id: int, user: CurrentUser, db: DbDep):
    model_repo = TrainedModelRepositoryImpl(db)
    use_case = SelectModelUseCase(model_repo)
    try:
        raw = use_case.execute(model_id)
    except ValueError as exc:
        raise AppException.not_found(str(exc))
    data = SelectModelResponse(**raw).model_dump(by_alias=True)
    return ApiResponseFactory.ok(data, "Modelo seleccionado correctamente")


# === Model Versioning Endpoints ===

@router.get("/versions")
def list_model_versions(
    user: CurrentUser,
    db: DbDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """List all model versions for yield-prediction."""
    version_repo = ModelVersionRepositoryImpl(db)
    use_case = ListModelVersionsUseCase(version_repo)
    versions = use_case.execute(offset=offset, limit=limit)
    data = [ModelVersionRead.model_validate(v).model_dump(by_alias=True) for v in versions]
    return ApiResponseFactory.ok(data, "Versiones del modelo obtenidas")


@router.get("/versions/{version_id}")
def get_model_version(version_id: int, user: CurrentUser, db: DbDep):
    """Get a specific model version by ID."""
    version_repo = ModelVersionRepositoryImpl(db)
    use_case = GetModelVersionUseCase(version_repo)
    version = use_case.execute(version_id)
    if not version:
        raise AppException.not_found("Versión de modelo no encontrada")
    data = ModelVersionRead.model_validate(version).model_dump(by_alias=True)
    return ApiResponseFactory.ok(data, "Versión de modelo obtenida")


@router.get("/runs")
def list_model_runs(
    user: CurrentUser,
    db: DbDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List recent model training runs."""
    run_repo = ModelRunRepositoryImpl(db)
    use_case = ListModelRunsUseCase(run_repo)
    runs = use_case.execute(offset=offset, limit=limit)
    data = [ModelRunRead.model_validate(r).model_dump(by_alias=True) for r in runs]
    return ApiResponseFactory.ok(data, "Runs de entrenamiento obtenidos")


@router.post("/promote")
def promote_model_version(payload: PromoteRequest, user: CurrentUser, db: DbDep):
    """Promote a candidate version to production."""
    use_case = PromoteModelUseCase(db)
    try:
        result = use_case.execute(payload.version_id)
    except ValueError as exc:
        raise AppException.bad_request(str(exc))
    return ApiResponseFactory.ok(result, "Versión promovida a producción")


@router.post("/rollback")
def rollback_model_version(payload: RollbackRequest, user: CurrentUser, db: DbDep):
    """Rollback to a previous model version."""
    use_case = RollbackModelUseCase(db)
    try:
        result = use_case.execute(payload.version_id)
    except ValueError as exc:
        raise AppException.bad_request(str(exc))
    return ApiResponseFactory.ok(result, "Rollback completado")


@router.get("/production")
def get_production_model(user: CurrentUser, db: DbDep):
    """Get the current production model version."""
    from app.infrastructure.ml.model_registry import get_registry
    registry = get_registry(db)
    model = registry.get_production_model()
    if not model:
        raise AppException.not_found("No hay modelo en producción")
    return ApiResponseFactory.ok(model, "Modelo en producción obtenido")