from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class ModelVersion(BitacoraMixin, Base):
    __tablename__ = "model_version"
    __table_args__ = {"schema": Schemas.CORE}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("core.company.id"), index=True, nullable=True
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("candidate", "production", "archived", name="model_version_status", create_type=True, schema=Schemas.CORE),
        nullable=False,
        server_default="candidate",
    )
    trained_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    git_commit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    data_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    data_from: Mapped[Date | None] = mapped_column(Date, nullable=True)
    data_to: Mapped[Date | None] = mapped_column(Date, nullable=True)
    features: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    candidates_evaluated: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    baseline_compared: Mapped[str | None] = mapped_column(String(50), nullable=True)
    base_version_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("core.model_version.id"), nullable=True)
    artifact_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)