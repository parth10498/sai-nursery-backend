import enum
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class PaymentModeEnum(str, enum.Enum):
    CASH = "cash"
    ONLINE = "online"
    CHEQUE = "cheque"
    BANK_TRANSFER = "bank_transfer"


class Payment(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "payments"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    payment_mode: Mapped[PaymentModeEnum] = mapped_column(
        Enum(PaymentModeEnum, name="payment_mode_enum", native_enum=False),
        default=PaymentModeEnum.CASH,
        nullable=False,
    )
    receipt_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    payment_proof_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    customer = relationship("User", back_populates="payments")
