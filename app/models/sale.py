import uuid
from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class Sale(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sales"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sugar_cane_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sugar_canes.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    unit_type: Mapped[str] = mapped_column(
        String(20),
        default="QTY",
        server_default="QTY",
        nullable=False,
        index=True,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    sale_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    customer = relationship("User", back_populates="sales")
    sugarcane = relationship("SugarCane", back_populates="sales")
