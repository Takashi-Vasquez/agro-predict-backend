"""
Integration tests for model_registry.py
"""
import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.ml.model_registry import ModelRegistry


class TestModelRegistry:
    """Test ModelRegistry class"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        db = Mock()
        db.execute = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        return db
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings"""
        with patch('app.infrastructure.ml.model_registry.get_settings') as mock:
            settings = Mock()
            settings.BASE_DIR = "/tmp/test"
            settings.ML_MODEL_PATH = "/tmp/test/ml/artifacts"
            mock.return_value = settings
            yield settings
    
    @pytest.fixture
    def registry(self, mock_db, mock_settings):
        """Create ModelRegistry instance with mocked dependencies"""
        with patch.object(ModelRegistry, '_load_config') as mock_load:
            mock_load.return_value = {
                "model": {
                    "name": "prediccion-rendimiento",
                    "algorithms": ["random_forest", "linear_regression"],
                    "promotion_metric": "rmse",
                    "promotion_tolerance": 0.01,
                    "random_seed": 42,
                },
                "training": {
                    "test_window_months": 6,
                    "min_train_records": 50,
                    "temporal_split_column": "created_at",
                },
                "artifacts": {
                    "base_path": "app/infrastructure/ml/artifacts/modelos",
                    "include_version_in_path": True,
                },
            }
            with patch('app.infrastructure.ml.model_registry.get_settings') as mock_settings:
                settings = Mock()
                settings.BASE_DIR = "/tmp/test"
                settings.ML_MODEL_PATH = "/tmp/test/ml/artifacts"
                mock_settings.return_value = settings
                
                registry = ModelRegistry(db=Mock())
                registry.db = Mock()
                registry.artifacts_base = Path("/tmp/test/artifacts/modelos")
                yield registry
    
    def test_get_current_version(self, registry):
        """Test getting current version from file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            version_file = Path(tmpdir) / "model_version.txt"
            version_file.write_text("1.3.0\n", encoding="utf-8")

            registry.base_dir = Path(tmpdir)
            version = registry.get_current_version()
            assert version == "1.3.0"
    
    def test_get_production_model(self, registry):
        """Test getting production model"""
        mock_row = Mock()
        mock_row.id = 1
        mock_row.version = "1.2.0"
        mock_row.metrics = {"rmse": 0.4, "mae": 0.3}
        mock_row.candidates_evaluated = {"random_forest": {"rmse": 0.4}}
        mock_row.artifact_path = "modelos/1.2.0/"
        mock_row.trained_at = "2026-01-15"
        
        registry.db.execute.return_value.fetchone.return_value = mock_row
        
        result = registry.get_production_model()
        
        assert result is not None
        assert result["version"] == "1.2.0"
        assert result["metrics"]["rmse"] == 0.4
    
    def test_get_production_model_none(self, registry):
        """Test getting production model when none exists"""
        registry.db.execute.return_value.fetchone.return_value = None
        
        result = registry.get_production_model()
        
        assert result is None
    
    def test_evaluate_candidates_rmse(self, registry):
        """Test candidate evaluation with RMSE (lower is better)"""
        candidates = {
            "random_forest": {"rmse": 0.42, "mae": 0.31, "r2": 0.85},
            "linear_regression": {"rmse": 0.55, "mae": 0.44, "r2": 0.78},
        }
        
        winner_name, winner_metrics, should_promote, improvement = registry.evaluate_candidates(candidates)
        
        assert winner_name == "random_forest"
        assert winner_metrics["rmse"] == 0.42
        assert should_promote is True  # No baseline to compare
    
    def test_evaluate_candidates_r2(self, registry):
        """Test candidate evaluation with R2 (higher is better)"""
        registry.config["model"]["promotion_metric"] = "r2"
        
        candidates = {
            "random_forest": {"rmse": 0.42, "mae": 0.31, "r2": 0.85},
            "linear_regression": {"rmse": 0.55, "mae": 0.44, "r2": 0.92},
        }
        
        winner_name, winner_metrics, should_promote, improvement = registry.evaluate_candidates(candidates)
        
        assert winner_name == "linear_regression"
        assert winner_metrics["r2"] == 0.92
    
    def test_evaluate_with_baseline_improvement(self, registry):
        """Test candidate evaluation with baseline comparison"""
        candidates = {
            "random_forest": {"rmse": 0.40, "mae": 0.30},
            "linear_regression": {"rmse": 0.55, "mae": 0.44},
        }
        baseline = {"rmse": 0.50, "mae": 0.35}
        
        winner_name, winner_metrics, should_promote, improvement = registry.evaluate_candidates(candidates, baseline)
        
        assert winner_name == "random_forest"
        assert improvement > 0  # 0.50 -> 0.40 = 20% improvement
        assert should_promote is True  # 20% > 1% tolerance
    
    def test_evaluate_with_baseline_no_improvement(self, registry):
        """Test candidate evaluation with baseline but no significant improvement"""
        candidates = {
            "random_forest": {"rmse": 0.496, "mae": 0.34},  # Only 0.8% improvement
        }
        baseline = {"rmse": 0.50, "mae": 0.35}
        
        winner_name, winner_metrics, should_promote, improvement = registry.evaluate_candidates(candidates, baseline)
        
        assert improvement < 0.01  # Less than 1% tolerance
        assert should_promote is False
    
    def test_create_version_artifacts(self, registry):
        """Test creating versioned artifact directory"""
        import joblib
        from sklearn.ensemble import RandomForestRegressor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            registry.artifacts_base = Path(tmpdir)
            
            # Create dummy model
            model = RandomForestRegressor(n_estimators=10, random_state=42)
            import numpy as np
            X = np.random.rand(100, 10)
            y = np.random.rand(100)
            model.fit(X, y)
            
            trained_models = {
                "random_forest": {
                    "model": model,
                    "metrics": {"rmse": 0.4, "mae": 0.3, "r2": 0.85},
                    "feature_importance": {"feat1": 0.5, "feat2": 0.3},
                    "hyperparameters": {"n_estimators": 100},
                    "training_samples": 1000,
                    "feature_names": ["feat1", "feat2"],
                }
            }
            
            artifact_path = registry.create_version_artifacts("1.3.0", trained_models)
            
            version_dir = Path(artifact_path)
            assert version_dir.exists()
            assert (version_dir / "random_forest.joblib").exists()
            assert (version_dir / "metadata.json").exists()
            
            # Verify metadata
            import json
            with open(version_dir / "metadata.json") as f:
                meta = json.load(f)
            assert meta["version"] == "1.3.0"
            assert "random_forest" in meta["models"]


class TestPromotionLogic:
    """Test promotion and rollback logic"""
    
    @pytest.fixture
    def mock_db(self):
        db = Mock()
        db.execute = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        return db
    
    def test_promote_validates_no_regression(self, mock_db):
        """Test that promotion validates no algorithm regression"""
        from app.infrastructure.ml.model_registry import ModelRegistry
        
        registry = ModelRegistry(db=mock_db)
        registry.db = mock_db
        
        # Mock current production
        prod_row = Mock()
        prod_row.id = 1
        prod_row.version = "1.2.0"
        prod_row.metrics = {"rmse": 0.40}
        prod_row.candidates_evaluated = {
            "random_forest": {"rmse": 0.40},
            "linear_regression": {"rmse": 0.55}
        }
        prod_row.trained_at = "2026-01-15"
        
        # Mock candidate
        cand_row = Mock()
        cand_row.id = 2
        cand_row.version = "1.3.0"
        cand_row.metrics = {"rmse": 0.45}
        cand_row.candidates_evaluated = {
            "random_forest": {"rmse": 0.45},  # Worse!
            "linear_regression": {"rmse": 0.50}
        }
        
        registry.db.execute.side_effect = [
            Mock(fetchone=Mock(return_value=cand_row)),  # get candidate (1st query)
            Mock(fetchone=Mock(return_value=prod_row)),  # get_production_model (2nd query)
        ]
        
        with pytest.raises(ValueError, match="worsen"):
            registry.promote_version(2)
    
    def test_promote_success(self, mock_db):
        """Test successful promotion"""
        from app.infrastructure.ml.model_registry import ModelRegistry
        
        registry = ModelRegistry(db=mock_db)
        registry.db = mock_db
        
        # Mock current production
        prod_row = Mock()
        prod_row.id = 1
        prod_row.version = "1.2.0"
        prod_row.metrics = {"rmse": 0.40}
        prod_row.candidates_evaluated = {
            "random_forest": {"rmse": 0.40},
            "linear_regression": {"rmse": 0.55}
        }
        prod_row.trained_at = "2026-01-15"
        
        # Mock candidate - better or equal
        cand_row = Mock()
        cand_row.id = 2
        cand_row.version = "1.3.0"
        cand_row.metrics = {"rmse": 0.38}
        cand_row.candidates_evaluated = {
            "random_forest": {"rmse": 0.38},  # Better!
            "linear_regression": {"rmse": 0.53}
        }
        
        registry.db.execute.side_effect = [
            Mock(fetchone=Mock(return_value=cand_row)),  # get candidate (1st query)
            Mock(fetchone=Mock(return_value=prod_row)),  # get_production_model (2nd query)
            Mock(),  # archive current
            Mock(),  # promote candidate
            Mock(),  # git tag version select
        ]
        
        result = registry.promote_version(2)
        
        assert result["success"] is True
        assert mock_db.commit.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])