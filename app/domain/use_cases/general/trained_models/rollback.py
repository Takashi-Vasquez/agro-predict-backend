"""
Rollback Model Version Use Case.
"""
from typing import Dict, Any
from app.infrastructure.ml.model_registry import ModelRegistry, get_registry


class RollbackModelUseCase:
    def __init__(self, db) -> None:
        self.registry = get_registry(db)

    def execute(self, version_id: int) -> Dict[str, Any]:
        """
        Rollback to a specific version.
        
        Args:
            version_id: ID of the model version to rollback to
            
        Returns:
            Dict with success status and message
            
        Raises:
            ValueError: If version not found or not rollback-eligible
        """
        return self.registry.rollback_version(version_id)