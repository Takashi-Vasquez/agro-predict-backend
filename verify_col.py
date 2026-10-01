from app.infrastructure.database.session import get_db
from sqlalchemy import inspect

db = next(get_db())
inspector = inspect(db.bind)
cols = inspector.get_columns('training_records', schema='core')
for c in cols:
    if c['name'] == 'is_trained':
        print(f"is_trained: type={c['type']}, nullable={c['nullable']}")
        break