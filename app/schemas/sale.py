from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


def _clean_unit_type(v: Optional[str]) -> str:
    if not v:
        return "QTY"
    val = v.strip().upper()
    if val not in ("QTY", "TONS"):
        raise ValueError("Unit type must be either 'QTY' (Plants) or 'TONS' (Metric Tons)")
    return val


def _validate_decimal_places(v: Optional[Decimal], field_name: str, max_places: int = 2) -> Optional[Decimal]:
    if v is None:
        return None
    if v <= Decimal("0"):
        raise ValueError(f"{field_name} must be greater than zero")
    # Check decimal places
    exponent = v.as_tuple().exponent
    if isinstance(exponent, int) and exponent < -max_places:
        raise ValueError(f"{field_name} cannot have more than {max_places} decimal places")
    return v


class SaleCreate(BaseModel):
    user_id: UUID = Field(..., description="Valid Customer ID")
    sugar_cane_id: Optional[UUID] = Field(None, description="Valid Sugarcane Variety ID")
    unit_type: str = Field("QTY", description="Unit type: 'QTY' (Plants) or 'TONS' (Metric Tons)")
    quantity: Decimal = Field(..., gt=0, le=Decimal("10000000.00"), description="Quantity sold")
    rate: Decimal = Field(..., gt=0, le=Decimal("1000000.00"), description="Rate per unit")
    sale_date: date = Field(..., description="Date of sale")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes or remarks")

    @field_validator("unit_type")
    @classmethod
    def validate_unit_type(cls, v: str) -> str:
        return _clean_unit_type(v)

    @field_validator("quantity")
    @classmethod
    def validate_qty(cls, v: Decimal) -> Decimal:
        return _validate_decimal_places(v, "Quantity", 2) # type: ignore

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: Decimal) -> Decimal:
        return _validate_decimal_places(v, "Rate", 2) # type: ignore

    @field_validator("sale_date")
    @classmethod
    def validate_sale_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Sale date cannot be in the future")
        if v < date(2000, 1, 1):
            raise ValueError("Sale date cannot be earlier than 01-Jan-2000")
        return v

    @field_validator("notes", mode="before")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and isinstance(v, str):
            s = v.strip()
            return s if s else None
        return v


class SaleUpdate(BaseModel):
    sugar_cane_id: Optional[UUID] = None
    unit_type: Optional[str] = None
    quantity: Optional[Decimal] = Field(None, gt=0, le=Decimal("10000000.00"))
    rate: Optional[Decimal] = Field(None, gt=0, le=Decimal("1000000.00"))
    sale_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("unit_type")
    @classmethod
    def validate_unit_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return _clean_unit_type(v)

    @field_validator("quantity")
    @classmethod
    def validate_qty(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        return _validate_decimal_places(v, "Quantity", 2)

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        return _validate_decimal_places(v, "Rate", 2)

    @field_validator("sale_date")
    @classmethod
    def validate_sale_date(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return None
        if v > date.today():
            raise ValueError("Sale date cannot be in the future")
        if v < date(2000, 1, 1):
            raise ValueError("Sale date cannot be earlier than 01-Jan-2000")
        return v

    @field_validator("notes", mode="before")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and isinstance(v, str):
            s = v.strip()
            return s if s else None
        return v


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
