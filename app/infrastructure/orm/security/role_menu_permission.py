from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class RoleMenuPermission(BitacoraMixin, Base):
    __tablename__ = "role_menu_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "menu_id", "permission_id", name="uq_role_menu_permission"),
        {"schema": Schemas.SECURITY},
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("security.roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
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

    role = relationship("Role", back_populates="role_menu_permissions", lazy="selectin")
    menu = relationship("Menu", back_populates="role_menu_permissions", lazy="selectin")
    permission = relationship("Permission", back_populates="role_menu_permissions", lazy="selectin")
