from fastapi import APIRouter
from app.api.deps import CurrentUser, DBSession
from app.schemas.base import ApiResponse
from app.schemas.dashboard import DashboardSummaryResponse, SalesAnalyticsResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=ApiResponse[DashboardSummaryResponse])
async def get_dashboard_summary(db: DBSession, user: CurrentUser):
    service = DashboardService(db)
    summary = await service.get_dashboard_summary()
    return ApiResponse(data=summary)


@router.get("/sales-analytics", response_model=ApiResponse[SalesAnalyticsResponse])
async def get_sales_analytics(db: DBSession, user: CurrentUser):
    service = DashboardService(db)
    summary = await service.get_dashboard_summary()
    return ApiResponse(data=summary.analytics)

