import sys
sys.path.insert(0, '/code')
from app.infrastructure.database.session import get_db
from sqlalchemy import inspect

db = next(get_db())
inspector = inspect(db.bind)

for table in ['model_version', 'model_run', 'predictions']:
    cols = inspector.get_columns(table, schema='core')
    print(f'=== {table} ===')
    for c in cols:
        print(f'  {c["name"]}: {c["type"]} nullable={c["nullable"]}')