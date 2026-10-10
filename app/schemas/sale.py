from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SaleCreate(BaseModel):
    user_id: UUID
    sugar_cane_id: Optional[UUID] = None
    unit_type: str = Field("QTY", description="Unit type: 'QTY' (Plants) or 'TONS' (Metric Tons)")
    quantity: Decimal = Field(..., gt=0, decimal_places=2)
    rate: Decimal = Field(..., gt=0, decimal_places=2)
    sale_date: date
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("sale_date")
    @classmethod
    def validate_sale_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Sale date cannot be in the future")
        return v


class SaleUpdate(BaseModel):
    sugar_cane_id: Optional[UUID] = None
    unit_type: Optional[str] = Field(None, description="Unit type: 'QTY' or 'TONS'")
    quantity: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    rate: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    sale_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)


class SaleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    customer_name: Optional[str] = None
    sugar_cane_id: Optional[UUID] = None
    sugarcane_name: Optional[str] = None
    unit_type: str = "QTY"
    quantity: Decimal
    rate: Decimal
    total_amount: Decimal
    sale_date: date
    notes: Optional[str] = None
    created_at: datetime
