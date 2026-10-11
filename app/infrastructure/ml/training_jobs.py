"""
Async training jobs with versioning integration.
"""
import logging
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from app.infrastructure.database.session import _get_session_factory
from app.infrastructure.repositories.general.trained_model_repository import TrainedModelRepositoryImpl
from app.infrastructure.repositories.general.training_record_repository import TrainingRecordRepositoryImpl
from app.infrastructure.ml.regression_trainer import train_models, save_versioned_artifacts
from app.infrastructure.ml.model_registry import ModelRegistry, get_registry
from app.infrastructure.config.settings import get_settings
from bump_version import VersionBumpContext

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=2)
_jobs: dict[str, dict] = {}
_lock = threading.Lock()


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


def _run_training_job(
    job_id: str,
    user_id: int,
    algorithms: Optional[list[str]],
    artifacts_dir: Path,
    bump_level: str = "patch",
    company_id: Optional[int] = None,
) -> None:
    if company_id is not None:
        from app.core.company_context import CompanyContext
        CompanyContext.set_empresa_id(company_id)

    with _lock:
        _jobs[job_id]["status"] = JobStatus.RUNNING
        _jobs[job_id]["started_at"] = datetime.utcnow().isoformat()
        _jobs[job_id]["bump_level"] = bump_level

    try:
        session_factory = _get_session_factory()
        db = session_factory()
        record_repo = TrainingRecordRepositoryImpl(db)
        records = []
        for r in record_repo.list_all(limit=10000):
            records.append({
                "nitrogen": r.nitrogen, "phosphorus": r.phosphorus, "potassium": r.potassium,
                "temperature": r.temperature, "humidity": r.humidity,
                "ph_soil": r.ph_soil, "rainfall": r.rainfall,
                "irrigation_type": r.irrigation_type, "variety": r.variety,
                "target_yield": r.target_yield,
            })
        db.close()

        if len(records) < 50:
            raise ValueError(f"Minimum 50 records required. Current: {len(records)}")

        # Train models with temporal split
        results = train_models(records, algorithms=algorithms)
        
        if not results:
            raise ValueError("Could not train models")

        # Get baseline (current production)
        registry = get_registry(session_factory())
        baseline = registry.get_production_model()
        
        # Evaluate candidates
        candidates_evaluated = {}
        for result in results:
            candidates_evaluated[result["algorithm"]] = {
                "rmse": result["rmse"],
                "mae": result["mae"],
                "r2": result["r2_score"],
            }
        
        # Select winner (best RMSE by default)
        metric = get_settings().MODEL_PROMOTION_METRIC if hasattr(get_settings(), 'MODEL_PROMOTION_METRIC') else "rmse"
        if metric in ("rmse", "mae"):
            winner = min(results, key=lambda x: x[metric])
        else:
            winner = max(results, key=lambda x: x[metric])
        
        winner_name = winner["algorithm"]
        winner_metrics = {
            "rmse": winner["rmse"],
            "mae": winner["mae"],
            "r2": winner["r2_score"],
        }
        
        # Compare with baseline
        baseline_metrics = None
        if baseline and baseline.get("metrics"):
            baseline_metrics = baseline["metrics"]
        
        # Check if winner beats baseline
        should_promote = True
        improvement = 0.0
        if baseline_metrics and "rmse" in baseline_metrics:
            improvement = (baseline_metrics["rmse"] - winner_metrics["rmse"]) / baseline_metrics["rmse"]
            tolerance = 0.01  # 1%
            should_promote = improvement >= tolerance

        git_commit = _get_git_commit()
        data_version = f"data_v{datetime.utcnow().strftime('%Y-%m-%d')}"
        data_from = "2018-01-01"
        data_to = datetime.utcnow().strftime("%Y-%m-%d")
        
        version_id = None
        new_version = None
        generated_version = False
        reason_no_version = None
        duration = 0
        
        start_time = datetime.utcnow()
        
        if should_promote:
            # Bump version
            try:
                with VersionBumpContext(bump_level) as new_version_str:
                    new_version = new_version_str
                    
                    # Save versioned artifacts
                    artifacts_base = Path(get_settings().ML_MODEL_PATH).parent / "modelos"
                    artifact_path = save_versioned_artifacts(results, new_version, artifacts_base)
                    
                    # Register version
                    registry = get_registry(session_factory())
                    version_id = registry.register_version(
                        version=new_version,
                        candidates_evaluated={
                            r["algorithm"]: {
                                "rmse": r["rmse"],
                                "mae": r["mae"],
                                "r2": r["r2_score"],
                            }
                            for r in results
                        },
                        winner_name=winner_name,
                        winner_metrics={
                            "rmse": winner["rmse"],
                            "mae": winner["mae"],
                            "r2": winner["r2_score"],
                        },
                        winner_algorithm=winner_name,
                        baseline_compared=baseline["version"] if baseline else None,
                        data_from="2018-01-01",
                        data_to=datetime.utcnow().strftime("%Y-%m-%d"),
                        features=[
                            "nitrogen", "phosphorus", "potassium", "temperature",
                            "humidity", "ph_soil", "rainfall",
                            "irrigation_type", "variety", "soil_type"
                        ],
                        artifact_path=f"modelos/{new_version}/",
                        git_commit=git_commit,
                        data_version=f"data_v{datetime.utcnow().strftime('%Y-%m-%d')}"
                    )
                    generated_version = True
            
            except Exception as e:
                logger.exception("Version bump failed")
                should_promote = False
                reason_no_version = f"version_bump_failed: {str(e)}"
        else:
            reason_no_version = "no_supero_baseline"

        # Register run
        duration = int((datetime.utcnow() - start_time).total_seconds())
        registry = get_registry(session_factory())
        registry.register_run(
            model_version_id=version_id,
            git_commit=git_commit,
            data_version=f"data_v{datetime.utcnow().strftime('%Y-%m-%d')}",
            data_from="2018-01-01",
            data_to=datetime.utcnow().strftime("%Y-%m-%d"),
            candidates_evaluated={
                r["algorithm"]: {
                    "rmse": r["rmse"],
                    "mae": r["mae"],
                    "r2": r["r2_score"],
                }
                for r in results
            },
            winner=winner_name,
            improvement_vs_baseline=improvement if should_promote else 0,
            generated_version=generated_version,
            reason_no_version=reason_no_version,
            duration_seconds=duration,
        )

        # Also save to legacy trained_models table
        version_ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        db2 = session_factory()
        model_repo = TrainedModelRepositoryImpl(db2)

        saved_models = []
        for i, result in enumerate(results):
            artifact_path = f"modelos/{new_version or version_ts}/{result['algorithm']}.joblib"
            is_best = i == 0
            if is_best:
                model_repo.archive_others()

            model_entity = model_repo.create(
                user_id=user_id,
                name=f"{result['algorithm']}_{version_ts}",
                algorithm=result["algorithm"],
                version=version_ts,
                r2_score=result["r2_score"],
                rmse=result["rmse"],
                mae=result["mae"],
                feature_importance=result["feature_importance"],
                hyperparameters=result["hyperparameters"],
                training_samples=result["training_samples"],
                feature_names=result["feature_names"],
                artifact_path=artifact_path,
                is_selected=is_best,
                notes="Versioned training" if generated_version else "Training run",
                status="ACTIVE",
            )
            saved_models.append(model_entity)
        db2.close()

        best = results[0] if results else None
        with _lock:
            _jobs[job_id]["status"] = JobStatus.COMPLETED
            _jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
            _jobs[job_id]["result"] = {
                "version": version_ts,
                "semantic_version": new_version,
                "best_algorithm": best["algorithm"] if best else None,
                "best_r2": best["r2_score"] if best else None,
                "models_count": len(saved_models),
                "candidates": {
                    r["algorithm"]: {
                        "rmse": r["rmse"],
                        "mae": r["mae"],
                        "r2": r["r2_score"],
                    }
                    for r in results
                },
                "winner": winner_name,
                "should_promote": should_promote,
                "bump_level": _jobs[job_id].get("bump_level", "patch"),
                "semantic_version_created": new_version is not None,
            }

    except Exception as exc:
        logger.exception("Training job %s failed", job_id)
        with _lock:
            _jobs[job_id]["status"] = JobStatus.FAILED
            _jobs[job_id]["error"] = str(exc)
            _jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()


def _get_git_commit() -> str:
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def submit_training_job(
    user_id: int,
    algorithms: Optional[list[str]] = None,
    record_repo_factory=None,
    model_repo_factory=None,
    artifacts_dir: Path = None,
    bump_level: str = "patch",
) -> str:
    from app.core.company_context import CompanyContext
    company_id = CompanyContext.get_empresa_id()

    job_id = str(uuid.uuid4())
    with _lock:
        _jobs[job_id] = {
            "id": job_id,
            "user_id": user_id,
            "status": JobStatus.PENDING,
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            "bump_level": bump_level,
        }

    _executor.submit(
        _run_training_job,
        job_id,
        user_id,
        algorithms,
        artifacts_dir,
        bump_level,
        company_id,
    )
    return job_id


def get_job_status(job_id: str, user_id: int) -> dict | None:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return None
        if job["user_id"] != user_id:
            return None
        return {
            "id": job["id"],
            "status": job["status"],
            "created_at": job["created_at"],
            "started_at": job["started_at"],
            "completed_at": job["completed_at"],
            "result": job["result"],
            "error": job["error"],
        }