import enum
from typing import List, Optional
from sqlalchemy import BigInteger, Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class UserTypeEnum(str, enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    type: Mapped[UserTypeEnum] = mapped_column(
        Enum(UserTypeEnum, name="user_type_enum", native_enum=False),
        default=UserTypeEnum.CUSTOMER,
        nullable=False,
        index=True,
    )
    mobile: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    country_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("countries.id", ondelete="SET NULL"), nullable=True)
    state_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("states.id", ondelete="SET NULL"), nullable=True)
    city_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("cities.id", ondelete="SET NULL"), nullable=True)
    pincode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    country = relationship("Country", lazy="selectin")
    state = relationship("State", lazy="selectin")
    city = relationship("City", lazy="selectin")

    sales: Mapped[List["Sale"]] = relationship("Sale", back_populates="customer", cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="customer", cascade="all, delete-orphan")
