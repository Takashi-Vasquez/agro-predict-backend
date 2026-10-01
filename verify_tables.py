import sys
sys.path.insert(0, '/code')
from app.infrastructure.database.session import get_db
from sqlalchemy import inspect, text

db = next(get_db())
inspector = inspect(db.bind)

for table in ['model_version', 'model_runs', 'predictions']:
    try:
        cols = inspector.get_columns(table, schema='core')
        print(f'=== {table} ===')
        for c in cols:
            print(f'  {c["name"]}: {c["type"]} nullable={c["nullable"]}')
    except Exception as e:
        print(f'=== {table} === ERROR: {e}')

# Check indexes
print('\n=== Indexes on model_version ===')
indexes = inspector.get_indexes('model_version', schema='core')
for idx in indexes:
    print(f'  {idx["name"]}: {idx["column_names"]} unique={idx["unique"]}')

# Check foreign keys
print('\n=== Foreign Keys on model_version ===')
fks = inspector.get_foreign_keys('model_version', schema='core')
for fk in fks:
    print(f'  {fk["name"]}: {fk["constrained_columns"]} -> {fk["referred_table"]}.{fk["referred_columns"]}')

print('\n=== Foreign Keys on predictions ===')
fks = inspector.get_foreign_keys('predictions', schema='core')
for fk in fks:
    print(f'  {fk["name"]}: {fk["constrained_columns"]} -> {fk["referred_table"]}.{fk["referred_columns"]}')

# Check enum values
print('\n=== Enum values ===')
result = db.execute(text("SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'model_version_status')"))
for row in result:
    print(f'  {row[0]}')