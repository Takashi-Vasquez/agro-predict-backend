"""
Promote Model Version Use Case.
"""
from typing import Dict, Any
from app.infrastructure.ml.model_registry import ModelRegistry, get_registry


class PromoteModelUseCase:
    def __init__(self, db) -> None:
        self.registry = get_registry(db)

    def execute(self, version_id: int) -> Dict[str, Any]:
        """
        Promote a candidate version to production.
        
        Args:
            version_id: ID of the model version to promote
            
        Returns:
            Dict with success status and message
            
        Raises:
            ValueError: If version not found, not in candidate state, 
                        or validation fails (algorithms worsen)
        """
        return self.registry.promote_version(version_id)