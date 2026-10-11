from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class Crop(BitacoraMixin, Base):
    __tablename__ = "crops"
    __table_args__ = {"schema": Schemas.OPERATIONS}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("security.users.id"), index=True, nullable=False)
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("core.company.id"), index=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    variety_id: Mapped[int] = mapped_column(ForeignKey("operations.varieties.id"), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    cycle: Mapped[int] = mapped_column(Integer, nullable=False)
    temperature: Mapped[str] = mapped_column(String(50), nullable=False)
    water: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(20), nullable=False)

    variety = relationship("Variety", lazy="selectin")
