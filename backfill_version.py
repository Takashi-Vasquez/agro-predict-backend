import sys
sys.path.insert(0, '/code')
from app.infrastructure.database.session import get_db
from sqlalchemy import text
import json
from datetime import datetime

db = next(get_db())

# Check if initial version exists
result = db.execute(text("SELECT id FROM core.model_version WHERE version = '1.0.0'"))
existing = result.fetchone()

if existing:
    print("Initial version 1.0.0 already exists")
else:
    # Insert initial version
    features = [
        "nitrogen", "phosphorus", "potassium", "temperature", "humidity",
        "ph_soil", "rainfall", "irrigation_type", "variety", "soil_type"
    ]
    
    candidates = {
        "random_forest": {
            "rmse": 0.5,
            "mae": 0.4,
            "artifact": "modelos/1.0.0/random_forest.joblib"
        },
        "linear_regression": {
            "rmse": 0.6,
            "mae": 0.5,
            "artifact": "modelos/1.0.0/linear_regression.joblib"
        }
    }
    
    metrics = {
        "rmse": 0.5,
        "mae": 0.4,
        "r2": 0.8
    }
    
    result = db.execute(text("""
        INSERT INTO core.model_version (
            model_name, version, status, trained_at, git_commit, data_version,
            data_from, data_to, features, candidates_evaluated, metrics,
            baseline_compared, base_version_id, artifact_path, created_at
        ) VALUES (
            'yield-prediction', '1.0.0', 'production', NOW(),
            'initial', 'data_initial', '2018-01-01', '2026-08-31',
            :features, :candidates, :metrics,
            NULL, NULL, 'modelos/1.0.0/', NOW()
        ) RETURNING id
    """), {
        'features': json.dumps(features),
        'candidates': json.dumps(candidates),
        'metrics': json.dumps(metrics)
    })
    
    version_id = result.fetchone()[0]
    db.commit()
    print(f"Inserted initial version 1.0.0 with id={version_id}")

    # Backfill predictions
    result = db.execute(text("""
        UPDATE core.predictions
        SET model_version_id = :version_id
        WHERE model_version_id IS NULL
    """), {'version_id': version_id})
    
    updated = result.rowcount
    db.commit()
    print(f"Backfilled {updated} predictions with model_version_id={version_id}")

print("Backfill complete")