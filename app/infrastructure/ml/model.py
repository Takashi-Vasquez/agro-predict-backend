import logging

import joblib
import numpy as np

logger = logging.getLogger(__name__)


class CropPredictor:
    def __init__(self, model_path, features) -> None:
        self.model_path = model_path
        self.features = list(features)
        self.model = None
        self.load()

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"No se encontro el modelo entrenado en: {self.model_path}. "
                "Ejecuta primero: python -m app.infrastructure.ml.train"
            )
        self.model = joblib.load(self.model_path)
        logger.info("Modelo cargado desde %s", self.model_path)

    def is_loaded(self) -> bool:
        return self.model is not None

    def predict(self, values: dict[str, float]) -> tuple[str, float]:
        if self.model is None:
            self.load()

        vector = np.array([[values[feature] for feature in self.features]])
        label = str(self.model.predict(vector)[0])
        proba = float(np.max(self.model.predict_proba(vector)[0]))
        return label, proba
