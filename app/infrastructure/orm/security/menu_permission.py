from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class MenuPermission(BitacoraMixin, Base):
    __tablename__ = "menu_permissions"
    __table_args__ = (
        UniqueConstraint("menu_id", "permission_id", name="uq_menu_permission"),
        {"schema": Schemas.SECURITY},
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    menu_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("security.menus.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    permission_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("security.permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    menu = relationship("Menu", back_populates="menu_permissions", lazy="selectin")
    permission = relationship("Permission", back_populates="menu_permissions", lazy="selectin")
