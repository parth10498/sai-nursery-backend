import math
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Query, status
from app.api.deps import AdminUser, CurrentUser, DBSession
from app.schemas.base import ApiResponse, PaginatedResponse
from app.schemas.sale import SaleCreate, SaleResponse, SaleUpdate
from app.services.sale_service import SaleService

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("", response_model=ApiResponse[PaginatedResponse[SaleResponse]])
async def list_sales(
    db: DBSession,
    user: CurrentUser,
    customer_id: Optional[UUID] = None,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    service = SaleService(db)
    sales, total = await service.list_sales(customer_id=customer_id, page=page, size=size)
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


@router.post("", response_model=ApiResponse[SaleResponse], status_code=status.HTTP_201_CREATED)
async def create_sale(payload: SaleCreate, db: DBSession, user: AdminUser):
    service = SaleService(db)
    sale = await service.create_sale(payload)
    return ApiResponse(data=sale, message="Sale recorded successfully")


@router.get("/{sale_id}", response_model=ApiResponse[SaleResponse])
async def get_sale(sale_id: UUID, db: DBSession, user: CurrentUser):
    service = SaleService(db)
    sale = await service.get_sale(sale_id)
    return ApiResponse(data=sale)


@router.put("/{sale_id}", response_model=ApiResponse[SaleResponse])
async def update_sale(sale_id: UUID, payload: SaleUpdate, db: DBSession, user: AdminUser):
    service = SaleService(db)
    sale = await service.update_sale(sale_id, payload)
    return ApiResponse(data=sale, message="Sale updated successfully")


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale(sale_id: UUID, db: DBSession, user: AdminUser):
    service = SaleService(db)
    await service.delete_sale(sale_id)
    return None
