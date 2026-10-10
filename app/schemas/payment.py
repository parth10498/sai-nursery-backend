from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.payment import PaymentModeEnum


class PaymentCreate(BaseModel):
    user_id: UUID
    amount_paid: Decimal = Field(..., gt=0, decimal_places=2)
    payment_date: date
    payment_mode: PaymentModeEnum = PaymentModeEnum.CASH
    receipt_no: Optional[str] = Field(None, max_length=50)
    payment_proof_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("payment_date")
    @classmethod
    def validate_payment_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Payment date cannot be in the future")
        return v


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
