import sys
sys.path.insert(0, '/code')
from app.infrastructure.database.session import get_db
from app.infrastructure.ml.model_registry import get_registry

db = next(get_db())
registry = get_registry(db)

# Test get_production_model
prod = registry.get_production_model()
print('Production model:', prod)

# Test list versions
from sqlalchemy import text
result = db.execute(text("""
    SELECT id, model_name, version, status, trained_at, metrics, candidates_evaluated
    FROM core.model_version
    WHERE model_name = 'yield-prediction'
    ORDER BY trained_at DESC
""")).fetchall()
for row in result:
    print(f'Version: {row.version}, Status: {row.status}, Trained: {row.trained_at}')
    print(f'  Metrics: {row.metrics}')
    print(f'  Candidates: {row.candidates_evaluated}')