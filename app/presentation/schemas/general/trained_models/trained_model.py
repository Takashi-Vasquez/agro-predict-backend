from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Optional, List, Dict, Any


class TrainRequest(BaseModel):
    algorithms: Optional[List[str]] = Field(
        default=None,
        description="Algorithms to train. Null = all available",
    )
    bump_level: str = Field(
        default="patch",
        description="Version bump level: patch, minor, major",
        pattern="^(patch|minor|major)$",
    )


class CandidateMetrics(BaseModel):
    rmse: float
    mae: float
    r2: float


class TrainResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    version: str
    semantic_version: Optional[str] = Field(default=None, alias="semanticVersion")
    best_algorithm: Optional[str] = Field(default=None, alias="bestAlgorithm")
    best_r2: Optional[float] = Field(default=None, alias="bestR2")
    models_count: int = Field(alias="modelsCount")
    models: List[Dict[str, Any]]
    candidates: Optional[Dict[str, CandidateMetrics]] = None
    winner: Optional[str] = None
    should_promote: Optional[bool] = Field(default=None, alias="shouldPromote")
    bump_level: str = Field(alias="bumpLevel")
    semantic_version_created: bool = Field(default=False, alias="semanticVersionCreated")


class TrainedModelRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    algorithm: str
    version: str
    r2_score: float = Field(alias="r2Score")
    rmse: float
    mae: float
    training_samples: int = Field(alias="trainingSamples")
    is_selected: bool = Field(alias="isSelected")
    created_at: Optional[str] = Field(default=None, alias="createdAt")


class TrainedModelDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    algorithm: str
    version: str
    r2_score: float = Field(alias="r2Score")
    rmse: float
    mae: float
    feature_importance: Optional[Dict[str, float]] = Field(default=None, alias="featureImportance")
    hyperparameters: Optional[Dict[str, Any]] = None
    training_samples: int = Field(alias="trainingSamples")
    feature_names: Optional[List[str]] = Field(default=None, alias="featureNames")
    is_selected: bool = Field(alias="isSelected")
    notes: Optional[str] = None
    created_at: Optional[str] = Field(default=None, alias="createdAt")


class SelectModelResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    algorithm: str
    is_selected: bool = Field(alias="isSelected")


class ModelVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    model_name: str = Field(alias="modelName")
    version: str
    status: str
    trained_at: Optional[datetime] = Field(default=None, alias="trainedAt")
    git_commit: Optional[str] = Field(default=None, alias="gitCommit")
    data_version: Optional[str] = Field(default=None, alias="dataVersion")
    data_from: Optional[date] = Field(default=None, alias="dataFrom")
    data_to: Optional[date] = Field(default=None, alias="dataTo")
    features: Optional[List[str]] = None
    candidates_evaluated: Optional[Dict[str, Dict[str, Any]]] = Field(default=None, alias="candidatesEvaluated")
    metrics: Optional[Dict[str, float]] = None
    baseline_compared: Optional[str] = Field(default=None, alias="baselineCompared")
    base_version_id: Optional[int] = Field(default=None, alias="baseVersionId")
    artifact_path: Optional[str] = Field(default=None, alias="artifactPath")


class ModelRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    model_version_id: Optional[int] = Field(default=None, alias="modelVersionId")
    trained_at: Optional[datetime] = Field(default=None, alias="trainedAt")
    git_commit: Optional[str] = Field(default=None, alias="gitCommit")
    data_version: Optional[str] = Field(default=None, alias="dataVersion")
    data_from: Optional[date] = Field(default=None, alias="dataFrom")
    data_to: Optional[date] = Field(default=None, alias="dataTo")
    candidates_evaluated: Optional[Dict[str, Dict[str, Any]]] = Field(default=None, alias="candidatesEvaluated")
    winner: Optional[str] = None
    improvement_vs_baseline: Optional[float] = Field(default=None, alias="improvementVsBaseline")
    generated_version: bool = Field(default=False, alias="generatedVersion")
    reason_no_version: Optional[str] = Field(default=None, alias="reasonNoVersion")
    duration_seconds: Optional[int] = Field(default=None, alias="durationSeconds")


class PromoteRequest(BaseModel):
    version_id: int = Field(alias="versionId")


class RollbackRequest(BaseModel):
    version_id: int = Field(alias="versionId")