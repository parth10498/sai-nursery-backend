from collections import defaultdict
from decimal import Decimal
from typing import Dict, List
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment
from app.models.sale import Sale
from app.models.sugar_cane import SugarCane
from app.models.user import User, UserTypeEnum
from app.schemas.dashboard import (
    CustomerDueSummary,
    DashboardKPIResponse,
    DashboardSummaryResponse,
    MonthlyVolumeTrend,
    SalesAnalyticsResponse,
    VarietySalesBreakdown,
)
from app.schemas.sale import SaleResponse
from app.services.customer_service import CustomerService


class DashboardService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_dashboard_summary(self) -> DashboardSummaryResponse:
        total_sales = await self._db.scalar(
            select(func.coalesce(func.sum(Sale.total_amount), 0)).where(Sale.deleted_at.is_(None))
        ) or Decimal("0.00")

        total_paid = await self._db.scalar(
            select(func.coalesce(func.sum(Payment.amount_paid), 0)).where(Payment.deleted_at.is_(None))
        ) or Decimal("0.00")

        balance = total_sales - total_paid

        customers_count = await self._db.scalar(
            select(func.count(User.id)).where(User.type == UserTypeEnum.CUSTOMER, User.deleted_at.is_(None))
        ) or 0

        sales_count = await self._db.scalar(
            select(func.count(Sale.id)).where(Sale.deleted_at.is_(None))
        ) or 0

        kpi = DashboardKPIResponse(
            total_sales_amount=Decimal(str(total_sales)),
            total_paid_amount=Decimal(str(total_paid)),
            total_pending_balance=Decimal(str(balance)),
            total_customers_count=customers_count,
            total_sales_count=sales_count,
        )

        # Sales Analytics by Units (QTY Plants vs TONS Weight)
        total_plants_qty = await self._db.scalar(
            select(func.coalesce(func.sum(Sale.quantity), 0)).where(
                Sale.deleted_at.is_(None), Sale.unit_type == "QTY"
            )
        ) or Decimal("0.00")

        total_tons_weight = await self._db.scalar(
            select(func.coalesce(func.sum(Sale.quantity), 0)).where(
                Sale.deleted_at.is_(None), Sale.unit_type == "TONS"
            )
        ) or Decimal("0.00")

        total_plants_amount = await self._db.scalar(
            select(func.coalesce(func.sum(Sale.total_amount), 0)).where(
                Sale.deleted_at.is_(None), Sale.unit_type == "QTY"
            )
        ) or Decimal("0.00")

        total_tons_amount = await self._db.scalar(
            select(func.coalesce(func.sum(Sale.total_amount), 0)).where(
                Sale.deleted_at.is_(None), Sale.unit_type == "TONS"
            )
        ) or Decimal("0.00")

        # Query all active sales to generate monthly trends and variety breakdown
        sales_stmt = (
            select(Sale)
            .options(selectinload(Sale.sugarcane))
            .where(Sale.deleted_at.is_(None))
            .order_by(Sale.sale_date.asc())
        )
        all_sales = (await self._db.execute(sales_stmt)).scalars().all()

        monthly_dict: Dict[str, Dict[str, Decimal]] = defaultdict(
            lambda: {"plants_qty": Decimal("0.00"), "tons_weight": Decimal("0.00"), "total_amount": Decimal("0.00")}
        )
        variety_dict: Dict[str, Dict[str, Decimal]] = defaultdict(
            lambda: {"plants_qty": Decimal("0.00"), "tons_weight": Decimal("0.00"), "total_amount": Decimal("0.00")}
        )

        for s in all_sales:
            m_key = s.sale_date.strftime("%b %y")
            v_name = s.sugarcane.name if s.sugarcane else "Unspecified Variety"

            if s.unit_type == "TONS":
                monthly_dict[m_key]["tons_weight"] += s.quantity
                variety_dict[v_name]["tons_weight"] += s.quantity
            else:
                monthly_dict[m_key]["plants_qty"] += s.quantity
                variety_dict[v_name]["plants_qty"] += s.quantity

            monthly_dict[m_key]["total_amount"] += s.total_amount
            variety_dict[v_name]["total_amount"] += s.total_amount

        monthly_trends = [
            MonthlyVolumeTrend(
                month=k,
                plants_qty=v["plants_qty"],
                tons_weight=v["tons_weight"],
                total_amount=v["total_amount"],
            )
            for k, v in monthly_dict.items()
        ]

        total_revenue = total_plants_amount + total_tons_amount
        variety_recovery_map = {
            "Co 86032 (Nira)": "12.8% Sugar Recovery | Drought Tolerant",
            "CoM 0265 (Phule 265)": "11.9% Sugar Recovery | Saline Tolerant",
            "MS 10001": "13.4% High Brix | Early Harvest",
            "Co 92005": "12.2% Sugar Recovery | Heavy Stalks",
        }

        variety_breakdown = []
        for v_name, v_data in variety_dict.items():
            pct = float((v_data["total_amount"] / total_revenue) * 100) if total_revenue > 0 else 0.0
            variety_breakdown.append(
                VarietySalesBreakdown(
                    variety_name=v_name,
                    plants_qty=v_data["plants_qty"],
                    tons_weight=v_data["tons_weight"],
                    total_amount=v_data["total_amount"],
                    percentage=round(pct, 1),
                    sugar_recovery=variety_recovery_map.get(v_name, "Standard Certified"),
                )
            )
        variety_breakdown.sort(key=lambda x: x.total_amount, reverse=True)

        analytics = SalesAnalyticsResponse(
            total_plants_qty=Decimal(str(total_plants_qty)),
            total_tons_weight=Decimal(str(total_tons_weight)),
            total_plants_amount=Decimal(str(total_plants_amount)),
            total_tons_amount=Decimal(str(total_tons_amount)),
            active_season="Kharif-Rabi '25-26",
            target_plants_qty=Decimal("200000.00"),
            plants_growth_percentage=18.4,
            avg_cane_weight_kg=1.34,
            brix_sugar_content=21.8,
            monthly_trends=monthly_trends,
            variety_breakdown=variety_breakdown,
        )

        recent_sales_stmt = (
            select(Sale)
            .options(selectinload(Sale.customer), selectinload(Sale.sugarcane))
            .where(Sale.deleted_at.is_(None))
            .order_by(Sale.sale_date.desc(), Sale.created_at.desc())
            .limit(5)
        )
        r_sales = (await self._db.execute(recent_sales_stmt)).scalars().all()
        recent_sales_responses = [
            SaleResponse(
                id=s.id,
                user_id=s.user_id,
                customer_name=s.customer.name if s.customer else None,
                sugar_cane_id=s.sugar_cane_id,
                sugarcane_name=s.sugarcane.name if s.sugarcane else None,
                unit_type=s.unit_type,
                quantity=s.quantity,
                rate=s.rate,
                total_amount=s.total_amount,
                sale_date=s.sale_date,
                notes=s.notes,
                created_at=s.created_at,
            )
            for s in r_sales
        ]

        cust_service = CustomerService(self._db)
        customers = (
            await self._db.execute(
                select(User).where(User.type == UserTypeEnum.CUSTOMER, User.deleted_at.is_(None))
            )
        ).scalars().all()

        due_list: List[CustomerDueSummary] = []
        for c in customers:
            _, _, bal = await cust_service.get_customer_totals(c.id)
            if bal > 0:
                due_list.append(
                    CustomerDueSummary(
                        customer_id=c.id,
                        customer_name=c.name,
                        mobile=c.mobile,
                        balance=bal,
                    )
                )

        due_list.sort(key=lambda x: x.balance, reverse=True)
        top_dues = due_list[:5]

        return DashboardSummaryResponse(
            kpis=kpi,
            recent_sales=recent_sales_responses,
            top_dues=top_dues,
            analytics=analytics,
        )
