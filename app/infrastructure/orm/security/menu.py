from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class Menu(BitacoraMixin, Base):
    __tablename__ = "menus"
    __table_args__ = {"schema": Schemas.SECURITY}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("security.menus.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    route: Mapped[str | None] = mapped_column(String(255), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    parent = relationship("Menu", remote_side="Menu.id", back_populates="children", lazy="selectin")
    children = relationship("Menu", back_populates="parent", lazy="selectin")
    menu_permissions = relationship("MenuPermission", back_populates="menu", lazy="selectin")
    role_menu_permissions = relationship("RoleMenuPermission", back_populates="menu", lazy="selectin")
