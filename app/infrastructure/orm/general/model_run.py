from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class ModelRun(BitacoraMixin, Base):
    __tablename__ = "model_run"
    __table_args__ = (
        Index("ix_model_run_trained_at", "trained_at"),
        {"schema": Schemas.CORE},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_version_id: Mapped[int | None] = mapped_column(ForeignKey("core.model_version.id"), nullable=True)
    trained_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    git_commit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    data_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    data_from: Mapped[Date | None] = mapped_column(Date, nullable=True)
    data_to: Mapped[Date | None] = mapped_column(Date, nullable=True)
    candidates_evaluated: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    winner: Mapped[str | None] = mapped_column(String(50), nullable=True)
    improvement_vs_baseline: Mapped[float | None] = mapped_column(nullable=True)
    generated_version: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    reason_no_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(nullable=True)