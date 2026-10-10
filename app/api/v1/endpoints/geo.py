from typing import List
from fastapi import APIRouter, Path
from app.api.deps import DBSession
from app.schemas.base import ApiResponse
from app.schemas.geo import CityResponse, CountryResponse, StateResponse
from app.services.geo_service import GeoService

router = APIRouter(prefix="/geo", tags=["Geolocation"])


@router.get("/countries", response_model=ApiResponse[List[CountryResponse]])
async def get_countries(db: DBSession):
    service = GeoService(db)
    countries = await service.get_countries()
    data = [CountryResponse.model_validate(c) for c in countries]
    return ApiResponse(data=data)


@router.get("/states/{country_id}", response_model=ApiResponse[List[StateResponse]])
async def get_states(
    country_id: int = Path(..., gt=0, description="Positive integer Country ID"),
    db: DBSession = None,
):
    service = GeoService(db)
    states = await service.get_states(country_id)
    data = [StateResponse.model_validate(s) for s in states]
    return ApiResponse(data=data)


@router.get("/cities/{state_id}", response_model=ApiResponse[List[CityResponse]])
async def get_cities(
    state_id: int = Path(..., gt=0, description="Positive integer State ID"),
    db: DBSession = None,
):
    service = GeoService(db)
    cities = await service.get_cities(state_id)
    data = [CityResponse.model_validate(c) for c in cities]
    return ApiResponse(data=data)
