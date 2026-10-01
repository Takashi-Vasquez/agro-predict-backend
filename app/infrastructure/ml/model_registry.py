"""
Model Registry - Core module for model versioning operations.

Handles:
- Version bumping (with rollback on failure)
- Model comparison and promotion gate
- Artifact management
- Promotion and rollback operations
- Run registration
"""

import json
import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.database.session import get_db
from app.infrastructure.config.settings import get_settings
from bump_version import bump_version, VersionBumpContext


class ModelRegistry:
    """Central registry for model versioning operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.artifacts_base = Path(self.settings.ML_MODEL_PATH).parent / "modelos"
        self.base_dir = Path(self.settings.ML_MODEL_PATH).parent.parent.parent
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration from YAML."""
        import yaml
        config_path = self.base_dir / "config" / "model_config.yaml"
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    
    def get_current_version(self) -> str:
        """Get current version from model_version.txt"""
        version_file = self.base_dir / "model_version.txt"
        if not version_file.exists():
            return "1.0.0"
        return version_file.read_text(encoding="utf-8").strip()
    
    def get_production_model(self) -> Optional[Dict[str, Any]]:
        """Get the current production model version info."""
        result = self.db.execute(text("""
            SELECT id, version, metrics, candidates_evaluated, artifact_path, trained_at
            FROM core.model_version
            WHERE model_name = 'yield-prediction' AND status = 'production'
        """)).fetchone()
        
        if result:
            return {
                "id": result.id,
                "version": result.version,
                "metrics": result.metrics,
                "candidates_evaluated": result.candidates_evaluated,
                "artifact_path": result.artifact_path,
                "trained_at": result.trained_at
            }
        return None
    
    def get_latest_candidate(self) -> Optional[Dict[str, Any]]:
        """Get the latest candidate model version."""
        result = self.db.execute(text("""
            SELECT id, version, metrics, candidates_evaluated, artifact_path, trained_at
            FROM core.model_version
            WHERE model_name = 'yield-prediction' AND status = 'candidate'
            ORDER BY trained_at DESC
            LIMIT 1
        """)).fetchone()
        
        if result:
            return {
                "id": result.id,
                "version": result.version,
                "metrics": result.metrics,
                "candidates_evaluated": result.candidates_evaluated,
                "artifact_path": result.artifact_path,
                "trained_at": result.trained_at
            }
        return None
    
    def evaluate_candidates(
        self,
        candidates: Dict[str, Dict[str, float]],
        baseline_metrics: Optional[Dict[str, float]] = None
    ) -> Tuple[str, Dict[str, Any], bool, float]:
        """
        Evaluate candidates and select winner.
        
        Returns:
            (winner_name, winner_metrics, should_promote, improvement)
        """
        metric_name = self.config["model"]["promotion_metric"]
        tolerance = self.config["model"]["promotion_tolerance"]
        
        # Select winner based on configured metric
        if metric_name == "rmse" or metric_name == "mae":
            winner = min(candidates.items(), key=lambda x: x[1].get(metric_name, float('inf')))
        else:  # r2
            winner = max(candidates.items(), key=lambda x: x[1].get(metric_name, -float('inf')))
        
        winner_name, winner_metrics = winner
        winner_value = winner_metrics.get(metric_name, 0)
        
        # Check against baseline
        should_promote = True
        improvement = 0.0
        
        if baseline_metrics and metric_name in baseline_metrics:
            baseline_value = baseline_metrics[metric_name]
            
            if metric_name in ("rmse", "mae"):
                # Lower is better
                improvement = (baseline_value - winner_value) / baseline_value
                should_promote = improvement >= self.config["model"]["promotion_tolerance"]
            else:  # r2
                # Higher is better
                improvement = (winner_value - baseline_value) / abs(baseline_value) if baseline_value != 0 else 0
                should_promote = improvement >= self.config["model"]["promotion_tolerance"]
        
        return winner_name, winner_metrics, should_promote, improvement
    
    def create_version_artifacts(
        self,
        version: str,
        trained_models: Dict[str, Any]
    ) -> str:
        """
        Create versioned artifact directory structure.
        
        Args:
            version: Semantic version string (e.g., "1.3.0")
            trained_models: Dict of trained model objects from regression_trainer
            
        Returns:
            Path to the version directory
        """
        version_dir = self.artifacts_base / version
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Save each model, scaler, imputer
        for algo_name, model_data in trained_models.items():
            if "model" in model_data:
                model_path = version_dir / f"{algo_name}.joblib"
                import joblib
                joblib.dump(model_data["model"], model_path)
            
            if "scaler" in model_data:
                scaler_path = version_dir / "scaler.joblib"
                import joblib
                joblib.dump(model_data["scaler"], scaler_path)
            
            if "imputer" in model_data:
                imputer_path = version_dir / "imputer.joblib"
                import joblib
                joblib.dump(model_data["imputer"], imputer_path)
        
        # Save metadata
        metadata = {
            "version": version,
            "created_at": datetime.utcnow().isoformat(),
            "models": {
                name: {
                    "algorithm": name,
                    "metrics": data.get("metrics", {}),
                    "feature_importance": data.get("feature_importance"),
                    "hyperparameters": data.get("hyperparameters"),
                    "training_samples": data.get("training_samples"),
                    "feature_names": data.get("feature_names"),
                }
                for name, data in trained_models.items()
            }
        }
        
        metadata_path = version_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return str(version_dir)
    
    def register_version(
        self,
        version: str,
        candidates_evaluated: Dict[str, Dict[str, Any]],
        winner_name: str,
        winner_metrics: Dict[str, float],
        winner_algorithm: str,
        baseline_compared: Optional[str],
        data_from: str,
        data_to: str,
        features: List[str],
        artifact_path: str,
        git_commit: Optional[str] = None,
        data_version: Optional[str] = None,
    ) -> int:
        """Register a new model version in the database."""
        # Prepare data
        features_json = json.dumps(features)
        
        # Prepare candidates_evaluated with artifact paths
        candidates_json = {}
        for name, metrics in self.config["model"]["algorithms"]:
            if name in trained_models:
                candidates_json[name] = {
                    "rmse": trained_models[name].get("metrics", {}).get("rmse", 0),
                    "mae": trained_models[name].get("metrics", {}).get("mae", 0),
                    "r2": trained_models[name].get("metrics", {}).get("r2", 0),
                    "artifact": f"modelos/{version}/{name}.joblib"
                }
        
        # For simplicity, use the provided candidates_evaluated
        candidates_json = json.dumps(candidates_evaluated)
        metrics_json = json.dumps(candidates_evaluated.get(winner_name, {}))
        features_json = json.dumps(features)
        
        result = self.db.execute(text("""
            INSERT INTO core.model_version (
                model_name, version, status, trained_at, git_commit, data_version,
                data_from, data_to, features, candidates_evaluated, metrics,
                baseline_compared, base_version_id, artifact_path, created_at
            ) VALUES (
                'yield-prediction', :version, 'candidate', NOW(),
                :git_commit, :data_version, :data_from, :data_to,
                :features, :candidates, :metrics,
                :baseline, NULL, :artifact_path, NOW()
            ) RETURNING id
        """), {
            'version': version,
            'git_commit': git_commit or self._get_git_commit(),
            'data_version': data_version or f"data_v{datetime.now().strftime('%Y-%m-%d')}",
            'data_from': data_from,
            'data_to': data_to,
            'features': features_json,
            'candidates': candidates_json,
            'metrics': metrics_json,
            'baseline': baseline_compared,
            'artifact_path': f"modelos/{version}/"
        })
        
        version_id = result.fetchone()[0]
        self.db.commit()
        return version_id
    
    def _get_git_commit(self) -> Optional[str]:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, cwd=self.base_dir
            )
            if result.returncode == 0:
                return result.stdout.strip()[:8]
        except Exception:
            pass
        return None
    
    def register_run(
        self,
        model_version_id: Optional[int],
        git_commit: str,
        data_version: str,
        data_from: str,
        data_to: str,
        candidates_evaluated: Dict[str, Dict[str, float]],
        winner: str,
        improvement_vs_baseline: float,
        generated_version: bool,
        reason_no_version: Optional[str] = None,
        duration_seconds: Optional[int] = None,
    ) -> int:
        """Register a training run (regardless of whether it produced a version)."""
        result = self.db.execute(text("""
            INSERT INTO core.model_runs (
                model_version_id, trained_at, git_commit, data_version,
                data_from, data_to, candidates_evaluated, winner,
                improvement_vs_baseline, generated_version, reason_no_version, duration_seconds
            ) VALUES (
                :model_version_id, NOW(), :git_commit, :data_version,
                :data_from, :data_to, :candidates, :winner,
                :improvement, :generated_version, :reason, :duration
            ) RETURNING id
        """), {
            'model_version_id': model_version_id,
            'git_commit': git_commit,
            'data_version': data_version,
            'data_from': data_from,
            'data_to': data_to,
            'candidates': json.dumps(candidates_evaluated),
            'winner': winner,
            'improvement': improvement_vs_baseline,
            'generated_version': generated_version,
            'reason': reason_no_version,
            'duration': duration_seconds
        })
        
        run_id = result.fetchone()[0]
        self.db.commit()
        return run_id
    
    def promote_version(self, version_id: int) -> Dict[str, Any]:
        """
        Promote a candidate version to production.
        Atomic operation: archive current production, promote candidate.
        Validates that no algorithm worsens compared to current production.
        """
        # Get the candidate version
        candidate = self.db.execute(text("""
            SELECT id, version, candidates_evaluated, metrics
            FROM core.model_version
            WHERE id = :id AND status = 'candidate'
        """), {'id': version_id}).fetchone()
        
        if not candidate:
            raise ValueError(f"Version {version_id} not found or not in 'candidate' state")
        
        # Get current production
        current_prod = self.get_production_model()
        
        # Validate: no algorithm should worsen
        if current_prod and current_prod.get("candidates_evaluated"):
            current_candidates = current_prod["candidates_evaluated"]
            new_candidates = candidate.candidates_evaluated
            
            for algo_name, new_metrics in new_candidates.items():
                if algo_name in current_candidates:
                    current_metrics = current_candidates[algo_name]
                    # Check RMSE (lower is better)
                    if new_metrics.get("rmse", 0) > current_metrics.get("rmse", 0) * 1.05:  # 5% tolerance
                        raise ValueError(
                            f"Algorithm {algo_name} would worsen RMSE: "
                            f"{new_metrics.get('rmse')} vs {current_metrics.get('rmse')}"
                        )
        
        # Atomic transaction: archive current + promote candidate
        try:
            # Archive current production
            if current_prod:
                self.db.execute(text("""
                    UPDATE core.model_version
                    SET status = 'archived'
                    WHERE model_name = 'yield-prediction' AND status = 'production'
                """))
            
            # Promote candidate
            self.db.execute(text("""
                UPDATE core.model_version
                SET status = 'production'
                WHERE id = :id
            """), {'id': version_id})
            
            self.db.commit()
            
            # Try to create git tag
            try:
                new_version = self.db.execute(text(
                    "SELECT version FROM core.model_version WHERE id = :id"
                ), {'id': version_id}).fetchone()[0]
                subprocess.run(
                    ["git", "tag", f"model-v{new_version}"],
                    cwd=self.base_dir,
                    check=False,
                    capture_output=True
                )
            except Exception:
                pass  # Don't fail if git tag fails
            
            return {"success": True, "message": "Version promoted to production"}
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Promotion failed: {str(e)}")
    
    def rollback_version(self, target_version_id: int) -> Dict[str, Any]:
        """Rollback to a specific version (archive current, promote target)."""
        # Get target version
        target = self.db.execute(text("""
            SELECT id, version FROM core.model_version
            WHERE id = :id AND status IN ('candidate', 'archived')
        """), {'id': target_version_id}).fetchone()
        
        if not target:
            raise ValueError(f"Version {target_version_id} not found or not rollback-eligible")
        
        # Same atomic operation as promote
        current_prod = self.get_production_model()
        
        try:
            if current_prod:
                self.db.execute(text("""
                    UPDATE core.model_version
                    SET status = 'archived'
                    WHERE model_name = 'yield-prediction' AND status = 'production'
                """))
            
            self.db.execute(text("""
                UPDATE core.model_version
                SET status = 'production'
                WHERE id = :id
            """), {'id': target_version_id})
            
            self.db.commit()
            
            return {"success": True, "message": f"Rolled back to version {target.version}"}
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Rollback failed: {str(e)}")


# Helper function for easy access
def get_registry(db: Session) -> ModelRegistry:
    return ModelRegistry(db)