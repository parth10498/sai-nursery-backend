import math
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Query, status
from app.api.deps import AdminUser, CurrentUser, DBSession
from app.schemas.base import ApiResponse, PaginatedResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("", response_model=ApiResponse[PaginatedResponse[PaymentResponse]])
async def list_payments(
    db: DBSession,
    user: CurrentUser,
    customer_id: Optional[UUID] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    service = PaymentService(db)
    payments, total = await service.list_payments(customer_id=customer_id, page=page, size=size)
    total_pages = math.ceil(total / size) if size > 0 else 0
    return ApiResponse(
        data=PaginatedResponse(
            items=payments,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )
    )


@router.post("", response_model=ApiResponse[PaymentResponse], status_code=status.HTTP_201_CREATED)
async def create_payment(payload: PaymentCreate, db: DBSession, user: AdminUser):
    service = PaymentService(db)
    payment = await service.create_payment(payload)
    return ApiResponse(data=payment, message="Payment recorded successfully")


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(payment_id: UUID, db: DBSession, user: AdminUser):
    service = PaymentService(db)
    await service.delete_payment(payment_id)
    return None
