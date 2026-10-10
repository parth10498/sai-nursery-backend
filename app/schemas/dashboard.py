from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.sale import SaleResponse


class DashboardKPIResponse(BaseModel):
    total_sales_amount: Decimal
    total_paid_amount: Decimal
    total_pending_balance: Decimal
    total_customers_count: int
    total_sales_count: int


class CustomerDueSummary(BaseModel):
    customer_id: UUID
    customer_name: str
    mobile: str | None = None
    balance: Decimal


class MonthlyVolumeTrend(BaseModel):
    month: str
    plants_qty: Decimal
    tons_weight: Decimal
    total_amount: Decimal


class VarietySalesBreakdown(BaseModel):
    variety_name: str
    plants_qty: Decimal
    tons_weight: Decimal
    total_amount: Decimal
    percentage: float
    sugar_recovery: Optional[str] = None


class SalesAnalyticsResponse(BaseModel):
    total_plants_qty: Decimal
    total_tons_weight: Decimal
    total_plants_amount: Decimal
    total_tons_amount: Decimal
    active_season: str = "Kharif-Rabi '25-26"
    target_plants_qty: Decimal = Decimal("200000.00")
    plants_growth_percentage: float = 18.4
    avg_cane_weight_kg: float = 1.34
    brix_sugar_content: float = 21.8
    monthly_trends: List[MonthlyVolumeTrend] = Field(default_factory=list)
    variety_breakdown: List[VarietySalesBreakdown] = Field(default_factory=list)


class DashboardSummaryResponse(BaseModel):
    kpis: DashboardKPIResponse
    recent_sales: List[SaleResponse]
    top_dues: List[CustomerDueSummary]
    analytics: SalesAnalyticsResponse

