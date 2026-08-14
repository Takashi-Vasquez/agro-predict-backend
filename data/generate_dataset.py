"""Genera un dataset sintetico de cultivos para el modelo predictivo.

Basado en el clasico dataset de recomendacion de cultivos (Kaggle).
Los rangos son aproximaciones razonables para la zona de clima templado.
"""

from pathlib import Path

import numpy as np
import pandas as pd

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

CROPS = [
    "rice", "maize", "chickpea", "kidneybeans", "pigeonpeas", "mothbeans",
    "mungbean", "blackgram", "lentil", "pomegranate", "banana", "mango",
    "grapes", "watermelon", "muskmelon", "apple", "orange", "papaya",
    "coconut", "cotton", "jute", "coffee",
]

# Perfiles de medias por cultivo (aproximados)
CROP_PROFILES = {
    "rice":        [80, 45, 40, 25, 80, 6.0, 200],
    "maize":       [75, 50, 60, 23, 65, 6.5, 90],
    "chickpea":    [25, 60, 35, 22, 55, 6.8, 90],
    "kidneybeans": [30, 60, 35, 22, 50, 6.8, 80],
    "pigeonpeas":  [25, 65, 40, 28, 50, 6.5, 120],
    "mothbeans":   [30, 65, 40, 30, 50, 6.5, 90],
    "mungbean":    [35, 55, 40, 28, 50, 6.5, 95],
    "blackgram":   [35, 60, 40, 30, 55, 6.5, 180],
    "lentil":      [20, 50, 35, 25, 55, 6.8, 120],
    "pomegranate": [25, 15, 20, 28, 45, 6.8, 110],
    "banana":      [120, 60, 50, 28, 85, 6.2, 150],
    "mango":       [20, 12, 15, 30, 60, 6.0, 140],
    "grapes":      [30, 30, 25, 28, 70, 6.6, 95],
    "watermelon":  [90, 40, 40, 30, 70, 6.4, 120],
    "muskmelon":   [90, 45, 40, 30, 70, 6.5, 30],
    "apple":       [35, 30, 40, 22, 85, 6.3, 100],
    "orange":      [20, 30, 60, 28, 85, 6.6, 120],
    "papaya":      [100, 60, 60, 30, 80, 6.4, 170],
    "coconut":     [20, 20, 20, 32, 90, 6.3, 200],
    "cotton":      [100, 45, 50, 28, 70, 6.5, 90],
    "jute":        [60, 40, 45, 28, 85, 6.3, 130],
    "coffee":      [90, 60, 50, 28, 75, 6.8, 100],
}


def generate_dataset(rows_per_crop: int = 250, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records = []
    for crop, center in CROP_PROFILES.items():
        center = np.asarray(center, dtype=float)
        for _ in range(rows_per_crop):
            noise = rng.normal(0, 1, size=len(FEATURES))
            noise = noise * np.asarray([4, 4, 4, 1.2, 3, 0.15, 6], dtype=float)
            sample = center + noise
            sample[0] = max(0, sample[0])
            sample[1] = max(0, sample[1])
            sample[2] = max(0, sample[2])
            sample[5] = np.clip(sample[5], 0, 14)
            records.append({**dict(zip(FEATURES, sample)), "label": crop})
    return pd.DataFrame(records)


def main() -> None:
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    df = generate_dataset()
    out = data_dir / "crop_data.csv"
    df.to_csv(out, index=False)
    print(f"Dataset generado: {out} ({df.shape[0]} filas, {df['label'].nunique()} cultivos)")


if __name__ == "__main__":
    main()