from typing import List
from uuid import UUID
from fastapi import APIRouter, Query, status
from app.api.deps import AdminUser, CurrentUser, DBSession
from app.schemas.base import ApiResponse
from app.schemas.sugar_cane import SugarCaneCreate, SugarCaneResponse, SugarCaneUpdate
from app.services.sugarcane_service import SugarCaneService

router = APIRouter(prefix="/sugarcane", tags=["Sugarcane Varieties"])


@router.get("", response_model=ApiResponse[List[SugarCaneResponse]])
async def list_varieties(
    db: DBSession,
    user: CurrentUser,
    active_only: bool = Query(False),
):
    service = SugarCaneService(db)
    varieties = await service.list_varieties(active_only=active_only)
    return ApiResponse(data=varieties)


@router.post("", response_model=ApiResponse[SugarCaneResponse], status_code=status.HTTP_201_CREATED)
async def create_variety(
    payload: SugarCaneCreate, db: DBSession, user: AdminUser
):
    service = SugarCaneService(db)
    variety = await service.create_variety(payload)
    return ApiResponse(data=variety, message="Variety created successfully")


@router.put("/{variety_id}", response_model=ApiResponse[SugarCaneResponse])
async def update_variety(
    variety_id: UUID, payload: SugarCaneUpdate, db: DBSession, user: AdminUser
):
    service = SugarCaneService(db)
    variety = await service.update_variety(variety_id, payload)
    return ApiResponse(data=variety, message="Variety updated successfully")


@router.delete("/{variety_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_variety(variety_id: UUID, db: DBSession, user: AdminUser):
    service = SugarCaneService(db)
    await service.delete_variety(variety_id)
    return None
