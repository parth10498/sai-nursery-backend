from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.payment import PaymentModeEnum


def _clean_str(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def _validate_decimal_places(v: Optional[Decimal], field_name: str, max_places: int = 2) -> Optional[Decimal]:
    if v is None:
        return None
    if v <= Decimal("0"):
        raise ValueError(f"{field_name} must be greater than zero")
    exponent = v.as_tuple().exponent
    if isinstance(exponent, int) and exponent < -max_places:
        raise ValueError(f"{field_name} cannot have more than {max_places} decimal places")
    return v


class PaymentCreate(BaseModel):
    user_id: UUID = Field(..., description="Customer ID")
    amount_paid: Decimal = Field(..., gt=0, le=Decimal("100000000.00"), description="Amount paid in INR")
    payment_date: date = Field(..., description="Date of payment")
    payment_mode: PaymentModeEnum = Field(default=PaymentModeEnum.CASH, description="Payment mode")
    receipt_no: Optional[str] = Field(None, max_length=50, description="Receipt / Reference number")
    payment_proof_url: Optional[str] = Field(None, max_length=500, description="URL or path to receipt proof")
    notes: Optional[str] = Field(None, max_length=500, description="Remarks")

    @field_validator("amount_paid")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        return _validate_decimal_places(v, "Amount paid", 2) # type: ignore

    @field_validator("payment_date")
    @classmethod
    def validate_payment_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Payment date cannot be in the future")
        if v < date(2000, 1, 1):
            raise ValueError("Payment date cannot be earlier than 01-Jan-2000")
        return v

    @field_validator("payment_mode", mode="before")
    @classmethod
    def validate_payment_mode(cls, v: object) -> object:
        if isinstance(v, str):
            val_clean = v.strip().lower()
            mode_map = {
                "cash": PaymentModeEnum.CASH,
                "online": PaymentModeEnum.ONLINE,
                "cheque": PaymentModeEnum.CHEQUE,
                "bank_transfer": PaymentModeEnum.BANK_TRANSFER,
                "bank transfer": PaymentModeEnum.BANK_TRANSFER,
                "neft": PaymentModeEnum.BANK_TRANSFER,
                "rtgs": PaymentModeEnum.BANK_TRANSFER,
                "upi": PaymentModeEnum.ONLINE,
            }
            if val_clean in mode_map:
                return mode_map[val_clean]
            valid_modes = [m.value for m in PaymentModeEnum]
            raise ValueError(f"Invalid payment mode '{v}'. Must be one of: {', '.join(valid_modes)}")
        return v

    @field_validator("receipt_no", "payment_proof_url", "notes", mode="before")
    @classmethod
    def clean_strings(cls, v: Optional[str]) -> Optional[str]:
        return _clean_str(v)


class PaymentUpdate(BaseModel):
    amount_paid: Optional[Decimal] = Field(None, gt=0, le=Decimal("100000000.00"))
    payment_date: Optional[date] = None
    payment_mode: Optional[PaymentModeEnum] = None
    receipt_no: Optional[str] = Field(None, max_length=50)
    payment_proof_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("amount_paid")
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        return _validate_decimal_places(v, "Amount paid", 2)

    @field_validator("payment_date")
    @classmethod
    def validate_payment_date(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return None
        if v > date.today():
            raise ValueError("Payment date cannot be in the future")
        if v < date(2000, 1, 1):
            raise ValueError("Payment date cannot be earlier than 01-Jan-2000")
        return v

    @field_validator("payment_mode", mode="before")
    @classmethod
    def validate_payment_mode(cls, v: object) -> object:
        if v is None:
            return None
        if isinstance(v, str):
            val_clean = v.strip().lower()
            mode_map = {
                "cash": PaymentModeEnum.CASH,
                "online": PaymentModeEnum.ONLINE,
                "cheque": PaymentModeEnum.CHEQUE,
                "bank_transfer": PaymentModeEnum.BANK_TRANSFER,
                "bank transfer": PaymentModeEnum.BANK_TRANSFER,
                "neft": PaymentModeEnum.BANK_TRANSFER,
                "rtgs": PaymentModeEnum.BANK_TRANSFER,
                "upi": PaymentModeEnum.ONLINE,
            }
            if val_clean in mode_map:
                return mode_map[val_clean]
            valid_modes = [m.value for m in PaymentModeEnum]
            raise ValueError(f"Invalid payment mode '{v}'. Must be one of: {', '.join(valid_modes)}")
        return v

    @field_validator("receipt_no", "payment_proof_url", "notes", mode="before")
    @classmethod
    def clean_strings(cls, v: Optional[str]) -> Optional[str]:
        return _clean_str(v)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    customer_name: Optional[str] = None
    amount_paid: Decimal
    payment_date: date
    payment_mode: PaymentModeEnum
    receipt_no: Optional[str] = None
    payment_proof_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
