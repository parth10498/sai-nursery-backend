from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    mobile: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    country_id: Optional[int] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None
    pincode: Optional[str] = Field(None, max_length=10)
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    mobile: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    country_id: Optional[int] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None
    pincode: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    state_name: Optional[str] = None
    city_name: Optional[str] = None
    total_sales: Decimal = Decimal("0.00")
    total_paid: Decimal = Decimal("0.00")
    balance: Decimal = Decimal("0.00")
    created_at: datetime


class CustomerLedgerResponse(BaseModel):
    customer_id: UUID
    customer_name: str
    total_sales: Decimal
    total_paid: Decimal
    balance: Decimal
    sales_count: int
    payments_count: int
