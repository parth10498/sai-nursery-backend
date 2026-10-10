from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    customers,
    dashboard,
    export_pdf,
    geo,
    payments,
    sales,
    sugar_cane,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(geo.router)
api_router.include_router(customers.router)
api_router.include_router(sugar_cane.router)
api_router.include_router(sales.router)
api_router.include_router(payments.router)
api_router.include_router(export_pdf.router)
