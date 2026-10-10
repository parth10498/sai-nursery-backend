from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class SugarCaneBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    code: Optional[str] = Field(None, max_length=50)
    default_rate: Decimal = Field(default=Decimal("0.00"), ge=0)
    description: Optional[str] = None
    is_active: bool = True


class SugarCaneCreate(SugarCaneBase):
    pass


class SugarCaneUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    code: Optional[str] = Field(None, max_length=50)
    default_rate: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SugarCaneResponse(SugarCaneBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
