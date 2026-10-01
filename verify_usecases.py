import sys
sys.path.insert(0, '/code')
from app.infrastructure.database.session import get_db
from app.domain.use_cases.general.trained_models.model_version import (
    GetModelVersionUseCase,
    ListModelVersionsUseCase,
    GetProductionModelUseCase,
)
from app.domain.use_cases.general.trained_models.model_run import ListModelRunsUseCase
from app.infrastructure.repositories.general.model_version_repository import ModelVersionRepositoryImpl
from app.infrastructure.repositories.general.model_run_repository import ModelRunRepositoryImpl

db = next(get_db())

# Test ListModelVersionsUseCase
version_repo = ModelVersionRepositoryImpl(db)
use_case = ListModelVersionsUseCase(version_repo)
versions = use_case.execute(offset=0, limit=10)
print("=== List Model Versions ===")
for v in versions:
    print(f"  Version: {v.version}, Status: {v.status}, Trained: {v.trained_at}")

# Test GetModelVersionUseCase
use_case = GetModelVersionUseCase(version_repo)
version = use_case.execute(1)
print(f"\n=== Get Model Version 1 ===")
print(f"  Version: {version.version}, Status: {version.status}")

# Test GetProductionModelUseCase
use_case = GetProductionModelUseCase(version_repo)
prod = use_case.execute()
print(f"\n=== Production Model ===")
print(f"  Version: {prod.version}, Status: {prod.status}")

# Test ListModelRunsUseCase
run_repo = ModelRunRepositoryImpl(db)
use_case = ListModelRunsUseCase(run_repo)
runs = use_case.execute(offset=0, limit=10)
print(f"\n=== Model Runs ===")
for r in runs:
    print(f"  ID: {r.id}, Winner: {r.winner}, Generated: {r.generated_version}, Reason: {r.reason_no_version}")