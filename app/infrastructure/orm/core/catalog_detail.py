from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class CatalogDetail(BitacoraMixin, Base):
    __tablename__ = "catalog_details"
    __table_args__ = {"schema": Schemas.CORE}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    catalog_id: Mapped[int] = mapped_column(
        ForeignKey("core.catalogs.id"), nullable=False, index=True
    )
    value: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(150), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
