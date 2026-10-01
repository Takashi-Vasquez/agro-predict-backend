import json
import logging
from pathlib import Path

import joblib
import numpy as np

logger = logging.getLogger(__name__)


class YieldPredictor:
    def __init__(self, model_dir: str | Path) -> None:
        self.model_dir = Path(model_dir)
        self.model = None
        self.scaler = None
        self.metadata = None
        self._load()

    def _load(self) -> None:
        model_path = self.model_dir / "model.joblib"
        scaler_path = self.model_dir / "scaler.joblib"
        imputer_path = self.model_dir / "imputer.joblib"
        meta_path = self.model_dir / "metadata.json"

        if not model_path.exists():
            raise FileNotFoundError(f"Modelo no encontrado: {model_path}")

        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path) if scaler_path.exists() else None
        self.imputer = joblib.load(imputer_path) if imputer_path.exists() else None

        if meta_path.exists():
            self.metadata = json.loads(meta_path.read_text())
        else:
            self.metadata = {}

        logger.info("Modelo cargado desde %s", self.model_dir)

    def predict(self, features: dict[str, float]) -> dict:
        if self.model is None:
            self._load()

        feature_names = self.metadata.get("feature_names", [])
        vector = []
        for fname in feature_names:
            vector.append(float(features.get(fname, 0.0)))

        X = np.array([vector])
        if self.imputer is not None:
            X = self.imputer.transform(X)
        if self.scaler is not None:
            X = self.scaler.transform(X)

        prediction = float(self.model.predict(X)[0])

        return {
            "predicted_yield": round(prediction, 2),
            "algorithm": self.metadata.get("algorithm", "unknown"),
            "r2_score": self.metadata.get("r2_score", 0.0),
        }
