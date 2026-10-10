from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CountryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: Optional[str] = None


class StateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    country_id: int
    name: str


class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    state_id: int
    name: str
