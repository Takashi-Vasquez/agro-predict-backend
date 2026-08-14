import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from app.infrastructure.config.settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    data_path = Path("data") / "crop_data.csv"

    if not data_path.exists():
        raise FileNotFoundError(
            f"No se encontro el dataset en {data_path}. "
            "Generalo con: python -m data.generate_dataset"
        )

    df = pd.read_csv(data_path)
    logger.info("Dataset cargado: %s filas, %s columnas", df.shape[0], df.shape[1])

    X = df[settings.ML_FEATURES]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    logger.info("Accuracy en test: %.4f", accuracy)
    logger.info("Reporte de clasificacion:\n%s", classification_report(y_test, model.predict(X_test)))

    settings.ML_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, settings.ML_MODEL_PATH)
    logger.info("Modelo guardado en %s", settings.ML_MODEL_PATH)


if __name__ == "__main__":
    main()
