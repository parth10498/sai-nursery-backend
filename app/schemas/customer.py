import re
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.payment import PaymentModeEnum


def _clean_str(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Customer full name")
    email: Optional[EmailStr] = None
    mobile: Optional[str] = Field(None, max_length=20, description="10-digit mobile number")
    address: Optional[str] = Field(None, max_length=500, description="Farm or residential address")
    country_id: Optional[int] = Field(None, gt=0, description="Valid Country ID")
    state_id: Optional[int] = Field(None, gt=0, description="Valid State ID")
    city_id: Optional[int] = Field(None, gt=0, description="Valid City / Taluka ID")
    pincode: Optional[str] = Field(None, max_length=10, description="6-digit PIN code")
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        s = v.strip() if isinstance(v, str) else ""
        if len(s) < 2:
            raise ValueError("Customer name must be at least 2 characters long")
        if len(s) > 150:
            raise ValueError("Customer name cannot exceed 150 characters")
        return s

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        return _clean_str(v)

    @field_validator("mobile", mode="before")
    @classmethod
    def validate_mobile(cls, v: Optional[str]) -> Optional[str]:
        cleaned = _clean_str(v)
        if not cleaned:
            return None
        # Remove spaces, hyphens, parentheses
        digits_only = re.sub(r"[\s\-\(\)]", "", cleaned)
        if digits_only.startswith("+91"):
            digits_only = digits_only[3:]
        elif digits_only.startswith("0") and len(digits_only) == 11:
            digits_only = digits_only[1:]

        if not re.match(r"^[6-9]\d{9}$", digits_only):
            raise ValueError("Mobile number must be a valid 10-digit Indian phone number starting with 6, 7, 8, or 9")
        return digits_only

    @field_validator("pincode", mode="before")
    @classmethod
    def validate_pincode(cls, v: Optional[str]) -> Optional[str]:
        cleaned = _clean_str(v)
        if not cleaned:
            return None
        if not re.match(r"^\d{6}$", cleaned):
            raise ValueError("Pincode must be exactly 6 digits (e.g. 416416)")
        return cleaned

    @field_validator("address", mode="before")
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        return _clean_str(v)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    mobile: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    country_id: Optional[int] = Field(None, gt=0)
    state_id: Optional[int] = Field(None, gt=0)
    city_id: Optional[int] = Field(None, gt=0)
    pincode: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = v.strip()
        if len(s) < 2:
            raise ValueError("Customer name must be at least 2 characters long")
        if len(s) > 150:
            raise ValueError("Customer name cannot exceed 150 characters")
        return s

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        return _clean_str(v)

    @field_validator("mobile", mode="before")
    @classmethod
    def validate_mobile(cls, v: Optional[str]) -> Optional[str]:
        cleaned = _clean_str(v)
        if not cleaned:
            return None
        digits_only = re.sub(r"[\s\-\(\)]", "", cleaned)
        if digits_only.startswith("+91"):
            digits_only = digits_only[3:]
        elif digits_only.startswith("0") and len(digits_only) == 11:
            digits_only = digits_only[1:]

        if not re.match(r"^[6-9]\d{9}$", digits_only):
            raise ValueError("Mobile number must be a valid 10-digit Indian phone number starting with 6, 7, 8, or 9")
        return digits_only

    @field_validator("pincode", mode="before")
    @classmethod
    def validate_pincode(cls, v: Optional[str]) -> Optional[str]:
        cleaned = _clean_str(v)
        if not cleaned:
            return None
        if not re.match(r"^\d{6}$", cleaned):
            raise ValueError("Pincode must be exactly 6 digits (e.g. 416416)")
        return cleaned

    @field_validator("address", mode="before")
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        return _clean_str(v)


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    state_name: Optional[str] = None
    city_name: Optional[str] = None
    total_sales: Decimal = Decimal("0.00")
    total_paid: Decimal = Decimal("0.00")
    balance: Decimal = Decimal("0.00")
    created_at: datetime


class CustomerLedgerTransaction(BaseModel):
    id: UUID
    transaction_date: date
    type: str  # "SALE" or "PAYMENT"
    reference_no: Optional[str] = None
    description: str
    debit: Decimal = Decimal("0.00")
    credit: Decimal = Decimal("0.00")
    running_balance: Decimal = Decimal("0.00")


class CustomerLedgerResponse(BaseModel):
    customer_id: UUID
    customer_name: str
    total_sales: Decimal
    total_paid: Decimal
    balance: Decimal
    sales_count: int
    payments_count: int
    transactions: List[CustomerLedgerTransaction] = Field(default_factory=list)


class CustomerStatementResponse(BaseModel):
    customer_id: UUID
    customer_name: str
    mobile: Optional[str] = None
    address: Optional[str] = None
    total_sales: Decimal
    total_paid: Decimal
    balance: Decimal
    status: str  # "SETTLED" or "PENDING"
    sales_count: int
    payments_count: int
    transactions: List[CustomerLedgerTransaction] = Field(default_factory=list)


class CustomerSettleRequest(BaseModel):
    amount: Optional[Decimal] = Field(
        None,
        gt=0,
        le=Decimal("100000000.00"),
        description="Amount to settle. If omitted or settle_full=True, settles exact outstanding balance",
    )
    settle_full: bool = Field(False, description="Whether to settle the full remaining outstanding balance")
    payment_mode: PaymentModeEnum = Field(default=PaymentModeEnum.CASH, description="Payment mode")
    payment_date: Optional[date] = Field(None, description="Settlement payment date (defaults to today)")
    receipt_no: Optional[str] = Field(None, max_length=50, description="Receipt or transaction reference number")
    payment_proof_url: Optional[str] = Field(None, max_length=500, description="URL or attachment proof")
    notes: Optional[str] = Field(None, max_length=500, description="Settlement remarks or waiver notes")

    @field_validator("payment_date")
    @classmethod
    def validate_payment_date(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Settlement payment date cannot be in the future")
        return v


class CustomerSettleResponse(BaseModel):
    payment_id: UUID
    customer_id: UUID
    customer_name: str
    previous_balance: Decimal
    amount_settled: Decimal
    remaining_balance: Decimal
    is_fully_settled: bool
    payment_date: date
    payment_mode: PaymentModeEnum
    receipt_no: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


class PendingDueCustomer(BaseModel):
    customer_id: UUID
    customer_name: str
    mobile: Optional[str] = None
    total_sales: Decimal
    total_paid: Decimal
    balance: Decimal
    sales_count: int
    payments_count: int


class PendingDuesSummaryResponse(BaseModel):
    total_pending_dues: Decimal
    total_unsettled_farmers: int
    items: List[PendingDueCustomer] = Field(default_factory=list)

