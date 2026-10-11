from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class RolePermissionDetail(BitacoraMixin, Base):
    __tablename__ = "role_permission_details"
    __table_args__ = (
        UniqueConstraint("role_permissions_id", "menu_id", "permission_id", name="uq_role_permission_detail"),
        {"schema": Schemas.SECURITY},
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_permissions_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("security.role_permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    menu_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("security.menus.id", ondelete="CASCADE"),
        nullable=False,
    )
    permission_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("security.permissions.id", ondelete="CASCADE"),
        nullable=False,
    )

    role_permission = relationship("RolePermission", back_populates="details", lazy="raise")
