from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class RolePermission(BitacoraMixin, Base):
    __tablename__ = "role_permissions"
    __table_args__ = {"schema": Schemas.SECURITY}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("core.company.id"), index=True, nullable=True
    )

    details = relationship("RolePermissionDetail", back_populates="role_permission", lazy="select")
