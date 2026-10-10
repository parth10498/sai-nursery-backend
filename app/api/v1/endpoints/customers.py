import math
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Query, status
from app.api.deps import AdminUser, DBSession
from app.schemas.base import ApiResponse, PaginatedResponse
from app.schemas.customer import (
    CustomerCreate,
    CustomerLedgerResponse,
    CustomerResponse,
    CustomerUpdate,
)
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=ApiResponse[PaginatedResponse[CustomerResponse]])
async def list_customers(
    db: DBSession,
    user: AdminUser,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    service = CustomerService(db)
    customers, total = await service.list_customers(search=search, page=page, size=size)
    total_pages = math.ceil(total / size) if size > 0 else 0
    return ApiResponse(
        data=PaginatedResponse(
            items=customers,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )
    )


@router.post("", response_model=ApiResponse[CustomerResponse], status_code=status.HTTP_201_CREATED)
async def create_customer(payload: CustomerCreate, db: DBSession, user: AdminUser):
    service = CustomerService(db)
    customer = await service.create_customer(payload)
    return ApiResponse(data=customer, message="Customer created successfully")


@router.get("/{customer_id}", response_model=ApiResponse[CustomerResponse])
async def get_customer(customer_id: UUID, db: DBSession, user: AdminUser):
    service = CustomerService(db)
    customer = await service.get_customer(customer_id)
    return ApiResponse(data=customer)


@router.put("/{customer_id}", response_model=ApiResponse[CustomerResponse])
async def update_customer(
    customer_id: UUID, payload: CustomerUpdate, db: DBSession, user: AdminUser
):
    service = CustomerService(db)
    customer = await service.update_customer(customer_id, payload)
    return ApiResponse(data=customer, message="Customer updated successfully")


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: UUID, db: DBSession, user: AdminUser):
    service = CustomerService(db)
    await service.delete_customer(customer_id)
    return None


@router.get("/{customer_id}/ledger", response_model=ApiResponse[CustomerLedgerResponse])
async def get_customer_ledger(customer_id: UUID, db: DBSession, user: AdminUser):
    service = CustomerService(db)
    ledger = await service.get_ledger(customer_id)
    return ApiResponse(data=ledger)
