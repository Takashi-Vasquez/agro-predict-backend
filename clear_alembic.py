from app.infrastructure.database.session import get_db
from sqlalchemy import text

db = next(get_db())
db.execute(text("DELETE FROM public.alembic_version;"))
db.commit()
print('Cleared alembic_version')