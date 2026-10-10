from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.sale import SaleResponse


def _clean_str(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def _validate_rate(v: Optional[Decimal]) -> Optional[Decimal]:
    if v is None:
        return None
    if v < Decimal("0"):
        raise ValueError("Default rate cannot be negative")
    exponent = v.as_tuple().exponent
    if isinstance(exponent, int) and exponent < -2:
        raise ValueError("Default rate cannot have more than 2 decimal places")
    return v


class SugarCaneBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Sugarcane variety name")
    code: Optional[str] = Field(None, max_length=50, description="Official variety code (e.g. CO-86032)")
    default_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=Decimal("1000000.00"), description="Default seedling rate in INR")
    description: Optional[str] = Field(None, max_length=1000, description="Variety description or regional notes")
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        s = v.strip() if isinstance(v, str) else ""
        if len(s) < 2:
            raise ValueError("Variety name must be at least 2 characters long")
        if len(s) > 150:
            raise ValueError("Variety name cannot exceed 150 characters")
        return s

    @field_validator("code", mode="before")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        cleaned = _clean_str(v)
        return cleaned.upper() if cleaned else None

    @field_validator("default_rate")
    @classmethod
    def validate_default_rate(cls, v: Decimal) -> Decimal:
        return _validate_rate(v) # type: ignore

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        return _clean_str(v)


class SugarCaneCreate(SugarCaneBase):
    pass


class SugarCaneUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    code: Optional[str] = Field(None, max_length=50)
    default_rate: Optional[Decimal] = Field(None, ge=0, le=Decimal("1000000.00"))
    description: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = v.strip()
        if len(s) < 2:
            raise ValueError("Variety name must be at least 2 characters long")
        if len(s) > 150:
            raise ValueError("Variety name cannot exceed 150 characters")
        return s

    @field_validator("code", mode="before")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        cleaned = _clean_str(v)
        return cleaned.upper() if cleaned else None

    @field_validator("default_rate")
    @classmethod
    def validate_default_rate(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        return _validate_rate(v)

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        return _clean_str(v)


class SugarCaneResponse(SugarCaneBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class SugarCaneDetailResponse(SugarCaneBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Purchase & Sales Analytics
    total_orders: int = 0
    total_revenue: Decimal = Decimal("0.00")
    total_plants_qty: Decimal = Decimal("0.00")
    total_tons_weight: Decimal = Decimal("0.00")
    unique_customers_count: int = 0
    first_sale_date: Optional[date] = None
    last_sale_date: Optional[date] = None

    # Purchase History
    recent_purchases: List[SaleResponse] = Field(default_factory=list)
