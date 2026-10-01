from datetime import datetime

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class TrainedModel(BitacoraMixin, Base):
    __tablename__ = "trained_models"
    __table_args__ = {"schema": Schemas.CORE}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    r2_score: Mapped[float] = mapped_column(Float, nullable=False)
    rmse: Mapped[float] = mapped_column(Float, nullable=False)
    mae: Mapped[float] = mapped_column(Float, nullable=False)
    feature_importance: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    hyperparameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    training_samples: Mapped[int] = mapped_column(Integer, nullable=False)
    feature_names: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    artifact_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
