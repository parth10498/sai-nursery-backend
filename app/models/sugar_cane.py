from typing import List, Optional
from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class SugarCane(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sugar_canes"

    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True, index=True)
    default_rate: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sales: Mapped[List["Sale"]] = relationship("Sale", back_populates="sugarcane")
