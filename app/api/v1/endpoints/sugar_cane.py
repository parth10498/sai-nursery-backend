import math
from typing import List
from uuid import UUID
from fastapi import APIRouter, Query, status
from app.api.deps import AdminUser, CurrentUser, DBSession
from app.schemas.base import ApiResponse, PaginatedResponse
from app.schemas.sale import SaleResponse
from app.schemas.sugar_cane import (
    SugarCaneCreate,
    SugarCaneDetailResponse,
    SugarCaneResponse,
    SugarCaneUpdate,
)
from app.services.sugarcane_service import SugarCaneService

router = APIRouter(prefix="/sugarcane", tags=["Sugarcane Varieties"])


@router.get("", response_model=ApiResponse[List[SugarCaneResponse]])
async def list_varieties(
    db: DBSession,
    user: CurrentUser,
    active_only: bool = Query(False, description="Filter only active varieties"),
):
    service = SugarCaneService(db)
    varieties = await service.list_varieties(active_only=active_only)
    return ApiResponse(data=varieties)


@router.get("/{variety_id}", response_model=ApiResponse[SugarCaneResponse])
async def get_variety(variety_id: UUID, db: DBSession, user: CurrentUser):
    service = SugarCaneService(db)
    variety = await service.get_variety(variety_id)
    return ApiResponse(data=variety)


@router.get("/{variety_id}/details", response_model=ApiResponse[SugarCaneDetailResponse])
async def get_variety_details(variety_id: UUID, db: DBSession, user: CurrentUser):
    """
    Get detailed information for a sugarcane variety including:
    - Audit logs & timestamps (created_at, updated_at, status)
    - Sales & purchase analytics (total orders, total revenue, plants qty, tons weight)
    - Recent customer purchases
    """
    service = SugarCaneService(db)
    details = await service.get_variety_details(variety_id)
    return ApiResponse(data=details)


@router.get("/{variety_id}/sales", response_model=ApiResponse[PaginatedResponse[SaleResponse]])
async def get_variety_sales(
    variety_id: UUID,
    db: DBSession,
    user: CurrentUser,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Get paginated purchase / sales history for this specific sugarcane variety.
    """
    service = SugarCaneService(db)
    sales, total = await service.list_variety_sales(variety_id=variety_id, page=page, size=size)
    total_pages = math.ceil(total / size) if size > 0 else 0
    return ApiResponse(
        data=PaginatedResponse(
            items=sales,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )
    )


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
