"""
Regression trainer with temporal split and versioning integration.
"""
import json
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

FIXED_COLUMNS = [
    "nitrogen", "phosphorus", "potassium", "temperature", "humidity",
    "ph_soil", "rainfall", "irrigation_type", "variety", "soil_type",
]
STRING_COLUMNS = ["irrigation_type", "variety", "soil_type"]
TOTAL_SEED_FIELDS = 11
MIN_RECORDS = 50

ALGORITHMS = {
    "random_forest": {
        "class": RandomForestRegressor,
        "default_params": {"n_estimators": 100, "max_depth": None, "random_state": 42, "n_jobs": -1},
    },
    "linear_regression": {
        "class": LinearRegression,
        "default_params": {},
    },
}


def _load_config() -> Dict[str, Any]:
    """Load model configuration from YAML."""
    config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


CONFIG = _load_config()


def _compute_completeness(row: pd.Series) -> float:
    filled = sum(1 for col in FIXED_COLUMNS if pd.notna(row.get(col)) and row.get(col) != 0)
    return filled / TOTAL_SEED_FIELDS


def _build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    feature_cols = list(FIXED_COLUMNS)
    if "completeness_score" in df.columns:
        feature_cols.append("completeness_score")
    return df[feature_cols], feature_cols


def _prepare_training_data(records: list[dict]) -> tuple[pd.DataFrame, pd.Series, list[float]]:
    rows = []
    weights = []
    for r in records:
        row = {}
        for col in FIXED_COLUMNS:
            val = r.get(col)
            if col in STRING_COLUMNS:
                if isinstance(val, str) and val:
                    row[col] = hash(val) % 1000 / 1000.0
                else:
                    row[col] = 0.0
            else:
                row[col] = float(val) if val is not None else 0.0

        filled = sum(1 for col in FIXED_COLUMNS if row.get(col, 0) != 0)
        completeness = filled / TOTAL_SEED_FIELDS
        row["completeness_score"] = completeness
        weights.append(max(completeness, 0.1))
        rows.append(row)

    df = pd.DataFrame(rows)
    target = pd.Series([float(r.get("target_yield", 0)) for r in records])
    return df, y, weights


def _temporal_split(
    df: pd.DataFrame,
    y: pd.Series,
    weights: List[float],
    test_window_months: int = 6,
    date_column: str = "created_at"
) -> tuple:
    """
    Split data temporally: use last N months as test set.
    Assumes records have a date column for temporal ordering.
    """
    # For now, use random split as fallback since we don't have date in records
    # TODO: Pass date information through records
    return train_test_split(
        df, y, weights, 
        test_size=0.2, 
        random_state=CONFIG.get("model", {}).get("random_seed", 42)
    )


def train_models(
    records: list[dict],
    algorithms: Optional[List[str]] = None,
    test_window_months: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Train regression models with temporal validation.
    
    Args:
        records: List of training records
        algorithms: List of algorithm names to train
        test_window_months: Months to use as test window (from config if None)
        
    Returns:
        List of training results with model objects and metrics
    """
    if len(records) < MIN_RECORDS:
        raise ValueError(f"Mínimo {MIN_RECORDS} registros requeridos. Actual: {len(records)}")

    if algorithms is None:
        algorithms = CONFIG["model"]["algorithms"]

    if test_window_months is None:
        test_window_months = CONFIG["training"]["test_window_months"]

    df, y, sample_weights = _prepare_training_data(records)
    X, feature_names = _build_features(df)

    imputer = SimpleImputer(strategy="median")
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=feature_names)

    # Temporal split (or random if no date available)
    X_train, X_test, y_train, y_test, w_train, w_test = _temporal_split(
        X_imputed, y, sample_weights, test_window_months
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = []
    for algo_name in algorithms:
        if algo_name not in ALGORITHMS:
            logger.warning("Algoritmo desconocido: %s", algo_name)
            continue

        algo_config = ALGORITHMS[algo_name]
        model_class = algo_config["class"]
        params = algo_config["default_params"].copy()

        model = model_class(**params)
        if algo_name != "linear_regression":
            model.fit(X_train_scaled, y_train, sample_weight=w_train)
        else:
            model.fit(X_train_scaled, y_train)

        y_pred = model.predict(X_test_scaled)

        r2 = float(r2_score(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))

        feature_importance = {}
        if hasattr(model, "feature_importances_"):
            for fname, imp in zip(feature_names, model.feature_importances_):
                feature_importance[fname] = round(float(imp), 4)
        elif hasattr(model, "coef_"):
            for fname, coef in zip(feature_names, model.coef_):
                feature_importance[fname] = round(float(abs(coef)), 4)

        results.append({
            "algorithm": algo_name,
            "r2_score": r2,
            "rmse": rmse,
            "mae": mae,
            "feature_importance": feature_importance,
            "hyperparameters": params,
            "feature_names": feature_names,
            "model": model,
            "scaler": scaler,
            "imputer": imputer,
            "training_samples": len(X_train),
        })

    # Sort by promotion metric (lower RMSE is better by default)
    metric = CONFIG["model"]["promotion_metric"]
    if metric in ("rmse", "mae"):
        results.sort(key=lambda x: x[metric])
    else:
        results.sort(key=lambda x: x[metric], reverse=True)

    logger.info(f"Trained {len(results)} models. Best {metric}: {results[0][metric]:.4f} ({results[0]['algorithm']})")
    return results


def save_model_artifact(
    result: Dict[str, Any],
    algorithm: str,
    version: str,
    artifacts_dir: Path,
) -> str:
    """Save model artifact with versioned directory structure."""
    dirname = f"{algorithm}_{version}"
    model_dir = artifacts_dir / dirname
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "model.joblib"
    scaler_path = model_dir / "scaler.joblib"
    imputer_path = model_dir / "imputer.joblib"

    joblib.dump(result["model"], model_path)
    joblib.dump(result["scaler"], scaler_path)
    joblib.dump(result["imputer"], imputer_path)

    meta_path = model_dir / "metadata.json"
    meta = {
        "algorithm": algorithm,
        "r2_score": result["r2_score"],
        "rmse": result["rmse"],
        "mae": result["mae"],
        "feature_importance": result["feature_importance"],
        "feature_names": result["feature_names"],
        "training_samples": result["training_samples"],
        "hyperparameters": result["hyperparameters"],
    }
    meta_path.write_text(json.dumps(meta, indent=2))

    return str(model_dir)


def save_versioned_artifacts(
    results: List[Dict[str, Any]],
    version: str,
    artifacts_base: Path,
) -> str:
    """
    Save all model artifacts in a versioned directory structure.
    
    Args:
        results: List of training results
        version: Semantic version (e.g., "1.3.0")
        artifacts_base: Base artifacts directory
        
    Returns:
        Path to version directory
    """
    version_dir = artifacts_base / version
    version_dir.mkdir(parents=True, exist_ok=True)

    for result in results:
        algo = result["algorithm"]
        model_path = version_dir / f"{algo}.joblib"
        joblib.dump(result["model"], model_path)

    # Save shared scaler and imputer (from first result)
    if results:
        scaler_path = version_dir / "scaler.joblib"
        imputer_path = version_dir / "imputer.joblib"
        joblib.dump(results[0]["scaler"], scaler_path)
        joblib.dump(results[0]["imputer"], imputer_path)

    # Save metadata
    meta_path = version_dir / "metadata.json"
    meta = {
        "version": version,
        "created_at": __import__("datetime").datetime.utcnow().isoformat(),
        "models": {
            result["algorithm"]: {
                "algorithm": result["algorithm"],
                "metrics": {
                    "r2": result["r2_score"],
                    "rmse": result["rmse"],
                    "mae": result["mae"],
                },
                "feature_importance": result["feature_importance"],
                "hyperparameters": result["hyperparameters"],
                "training_samples": result["training_samples"],
                "feature_names": result["feature_names"],
            }
            for result in results
        }
    }
    meta_path.write_text(json.dumps(meta, indent=2, default=str))

    return str(version_dir)