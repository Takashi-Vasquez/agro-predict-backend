"""
Train Models Use Case with versioning support.
"""
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from app.domain.repositories.general.trained_model_repository import TrainedModelRepository
from app.domain.repositories.general.training_record_repository import TrainingRecordRepository
from app.infrastructure.ml.regression_trainer import train_models, save_model_artifact
from app.infrastructure.ml.model_registry import ModelRegistry, get_registry
from app.infrastructure.config.settings import get_settings
from app.domain.use_cases.general.training_records.list_records import ListTrainingRecordsUseCase
from bump_version import VersionBumpContext


class TrainModelsUseCase:
    def __init__(
        self,
        record_repo: TrainingRecordRepository,
        model_repo: TrainedModelRepository,
        artifacts_dir: Path,
        bump_level: str = "patch",
        db: Any = None,
    ) -> None:
        self.record_repo = record_repo
        self.model_repo = model_repo
        self.artifacts_dir = artifacts_dir
        self.bump_level = bump_level.lower()
        self.db = db
        self.registry = get_registry(db) if db else None

    def execute(
        self,
        algorithms: List[str] | None = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        # Get records for training
        records = self._get_records_as_dicts()
        if not records:
            raise ValueError("No training records available")
        
        # Check minimum records
        min_records = get_settings().MODEL_MIN_TRAIN_RECORDS if hasattr(get_settings(), 'MODEL_MIN_TRAIN_RECORDS') else 50
        if len(records) < min_records:
            raise ValueError(f"Minimum {min_records} records required. Current: {len(records)}")

        # Train models
        results = train_models(records, algorithms=algorithms)
        
        if not results:
            raise ValueError("Could not train models")
        
        # Get baseline (current production)
        baseline = None
        if self.registry:
            baseline = self.registry.get_production_model()
        
        # Prepare candidates evaluation
        candidates_evaluated = {}
        for result in results:
            candidates_evaluated[result["algorithm"]] = {
                "rmse": result["rmse_score"],
                "mae": result["mae"],
                "r2": result["r2_score"],
            }
        
        # Select winner (best RMSE by default)
        winner_name = min(results, key=lambda r: r["rmse_score"])["algorithm"]
        winner_result = next(r for r in results if r["algorithm"] == winner_name)
        winner_metrics = {
            "rmse": winner_result["rmse_score"],
            "mae": winner_result["mae"],
            "r2": winner_result["r2_score"],
        }
        
        # Compare with baseline
        baseline_metrics = None
        if baseline and baseline.get("metrics"):
            baseline_metrics = baseline["metrics"]
        
        # Evaluate candidates
        from app.infrastructure.ml.model_registry import get_registry
        registry = self.registry
        if not self.registry and self.db:
            from app.infrastructure.ml.model_registry import get_registry
            registry = get_registry(self.db)
        
        # Compare winner vs baseline
        should_promote = True
        improvement = 0.0
        if registry and baseline and baseline.get("metrics"):
            metric_name = "rmse"
            baseline_value = baseline["metrics"].get("rmse", float('inf'))
            winner_value = winner_metrics.get("rmse", 0)
            
            if baseline_metrics and "rmse" in baseline["metrics"]:
                improvement = (baseline["metrics"]["rmse"] - winner_metrics["rmse"]) / baseline["metrics"]["rmse"]
                tolerance = 0.01  # 1%
                should_promote = improvement >= tolerance
        
        # Get version bump
        git_commit = self._get_git_commit()
        data_version = f"data_v{datetime.utcnow().strftime('%Y-%m-%d')}"
        data_from = "2018-01-01"
        data_to = datetime.utcnow().strftime("%Y-%m-%d")
        
        version_id = None
        new_version = None
        generated_version = False
        reason_no_version = None
        
        if should_promote:
            # Bump version
            try:
                with VersionBumpContext(self.bump_level) as new_version_str:
                    new_version = new_version_str
                    
                    # Create versioned artifacts
                    version_dir = f"modelos/{new_version}/"
                    artifact_base = Path(self.artifacts_dir).parent / "modelos" / new_version
                    artifact_base.mkdir(parents=True, exist_ok=True)
                    
                    # Save artifacts for each model
                    for result in results:
                        algo_name = result["algorithm"]
                        artifact_path = save_model_artifact(
                            result, algo_name, new_version, 
                            Path(self.artifacts_dir).parent / "modelos"
                        )
                    
                    # Register version
                    if self.registry:
                        version_id = self.registry.register_version(
                            version=new_version,
                            candidates_evaluated={
                                algo: {
                                    "rmse": r["rmse_score"],
                                    "mae": r["mae"],
                                    "r2": r["r2_score"],
                                }
                                for r in results
                            },
                            winner_name=winner_name,
                            winner_metrics={
                                "rmse": winner_metrics["rmse"],
                                "mae": winner_metrics["mae"],
                                "r2": winner_metrics["r2"],
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
                            git_commit=self._get_git_commit(),
                            data_version=f"data_v{datetime.utcnow().strftime('%Y-%m-%d')}"
                        )
                        generated_version = True
            
            except Exception as e:
                # Version bump failed - rollback handled by context manager
                raise ValueError(f"Version bump failed: {str(e)}")
        else:
            reason_no_version = "no_supero_baseline"
        
        # Register run
        duration = int(time.time() - start_time)
        if self.registry:
            self.registry.register_run(
                model_version_id=version_id,
                git_commit=self._get_git_commit() or "unknown",
                data_version=f"data_v{datetime.utcnow().strftime('%Y-%m-%d')}",
                data_from="2018-01-01",
                data_to=datetime.utcnow().strftime("%Y-%m-%d"),
                candidates_evaluated={
                    r["algorithm"]: {
                        "rmse": r["rmse_score"],
                        "mae": r["mae"],
                        "r2": r["r2_score"],
                    }
                    for r in results
                },
                winner=winner_name,
                improvement_vs_baseline=improvement,
                generated_version=generated_version,
                reason_no_version=reason_no_version,
                duration_seconds=duration,
            )
        
        # Save models to database (existing logic)
        version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        saved_models = []
        
        for i, result in enumerate(results):
            artifact_path = save_model_artifact(result, result["algorithm"], version, self.artifacts_dir)
            is_best = i == 0
            
            if is_best:
                self.model_repo.archive_others()
            
            model_entity = self.model_repo.create(
                user_id=0,  # System user for versioned training
                name=f"{result['algorithm']}_{version}",
                algorithm=result["algorithm"],
                version=version,
                r2_score=result["r2_score"],
                rmse=result["rmse_score"],
                mae=result["mae"],
                feature_importance=result["feature_importance"],
                hyperparameters=result["hyperparameters"],
                training_samples=result["training_samples"],
                feature_names=result["feature_names"],
                artifact_path=artifact_path,
                is_selected=is_best,
                notes="Versioned training",
                status="ACTIVE",
            )
            saved_models.append(model_entity)
        
        best = results[0] if results else None
        return {
            "version": version,
            "semantic_version": new_version,
            "best_algorithm": best["algorithm"] if best else None,
            "best_r2": best["r2_score"] if best else None,
            "models_count": len(saved_models),
            "models": [
                {
                    "id": m.id,
                    "algorithm": m.algorithm,
                    "r2_score": m.r2_score,
                    "rmse": m.rmse,
                    "mae": m.mae,
                    "is_selected": m.is_selected,
                }
                for m in saved_models
            ],
            "bump_level": self.bump_level,
            "semantic_version_created": new_version is not None,
            "candidates": candidates_evaluated,
            "winner": winner_name,
            "should_promote": should_promote,
        }

    def _get_records_as_dicts(self) -> List[Dict[str, Any]]:
        records = self.record_repo.list_all(limit=10000)
        result = []
        for r in records:
            d = {
                "nitrogen": r.nitrogen,
                "phosphorus": r.phosphorus,
                "potassium": r.potassium,
                "temperature": r.temperature,
                "humidity": r.humidity,
                "ph_soil": r.ph_soil,
                "rainfall": r.rainfall,
                "irrigation_type": r.irrigation_type,
                "variety": r.variety,
                "target_yield": r.target_yield,
            }
            result.append(d)
        return result
    
    def _get_git_commit(self) -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"