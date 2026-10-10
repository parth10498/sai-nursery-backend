from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sale import Sale
from app.models.sugar_cane import SugarCane
from app.schemas.sale import SaleResponse
from app.schemas.sugar_cane import (
    SugarCaneCreate,
    SugarCaneDetailResponse,
    SugarCaneResponse,
    SugarCaneUpdate,
)


class SugarCaneService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def list_varieties(self, active_only: bool = False) -> List[SugarCaneResponse]:
        stmt = select(SugarCane).where(SugarCane.deleted_at.is_(None)).order_by(SugarCane.name.asc())
        if active_only:
            stmt = stmt.where(SugarCane.is_active.is_(True))

        result = await self._db.execute(stmt)
        varieties = result.scalars().all()
        return [SugarCaneResponse.model_validate(v) for v in varieties]

    async def get_variety(self, variety_id: UUID) -> SugarCaneResponse:
        variety = await self._db.get(SugarCane, variety_id)
        if not variety or variety.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugarcane variety not found")
        return SugarCaneResponse.model_validate(variety)

    async def get_variety_details(self, variety_id: UUID) -> SugarCaneDetailResponse:
        variety = await self._db.get(SugarCane, variety_id)
        if not variety or variety.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugarcane variety not found")

        # Aggregate purchase / sales history stats
        stats_stmt = (
            select(
                func.count(Sale.id).label("total_orders"),
                func.coalesce(func.sum(Sale.total_amount), 0).label("total_revenue"),
                func.coalesce(
                    func.sum(case((func.upper(Sale.unit_type) == "QTY", Sale.quantity), else_=0)), 0
                ).label("total_plants_qty"),
                func.coalesce(
                    func.sum(case((func.upper(Sale.unit_type) == "TONS", Sale.quantity), else_=0)), 0
                ).label("total_tons_weight"),
                func.count(func.distinct(Sale.user_id)).label("unique_customers"),
                func.min(Sale.sale_date).label("first_sale_date"),
                func.max(Sale.sale_date).label("last_sale_date"),
            )
            .where(Sale.sugar_cane_id == variety_id, Sale.deleted_at.is_(None))
        )
        stats_res = (await self._db.execute(stats_stmt)).first()

        # Fetch recent purchases / orders
        recent_sales_stmt = (
            select(Sale)
            .options(selectinload(Sale.customer))
            .where(Sale.sugar_cane_id == variety_id, Sale.deleted_at.is_(None))
            .order_by(Sale.sale_date.desc(), Sale.created_at.desc())
            .limit(10)
        )
        recent_sales_result = await self._db.execute(recent_sales_stmt)
        sales_records = recent_sales_result.scalars().all()

        recent_purchases: List[SaleResponse] = []
        for s in sales_records:
            recent_purchases.append(
                SaleResponse(
                    id=s.id,
                    user_id=s.user_id,
                    customer_name=s.customer.name if s.customer else None,
                    sugar_cane_id=s.sugar_cane_id,
                    sugarcane_name=variety.name,
                    unit_type=s.unit_type,
                    quantity=s.quantity,
                    rate=s.rate,
                    total_amount=s.total_amount,
                    sale_date=s.sale_date,
                    notes=s.notes,
                    created_at=s.created_at,
                )
            )

        return SugarCaneDetailResponse(
            id=variety.id,
            name=variety.name,
            code=variety.code,
            default_rate=variety.default_rate,
            description=variety.description,
            is_active=variety.is_active,
            created_at=variety.created_at,
            updated_at=variety.updated_at,
            total_orders=stats_res.total_orders if stats_res else 0,
            total_revenue=Decimal(str(stats_res.total_revenue)) if stats_res else Decimal("0.00"),
            total_plants_qty=Decimal(str(stats_res.total_plants_qty)) if stats_res else Decimal("0.00"),
            total_tons_weight=Decimal(str(stats_res.total_tons_weight)) if stats_res else Decimal("0.00"),
            unique_customers_count=stats_res.unique_customers if stats_res else 0,
            first_sale_date=stats_res.first_sale_date if stats_res else None,
            last_sale_date=stats_res.last_sale_date if stats_res else None,
            recent_purchases=recent_purchases,
        )

    async def list_variety_sales(
        self,
        variety_id: UUID,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[SaleResponse], int]:
        variety = await self._db.get(SugarCane, variety_id)
        if not variety or variety.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugarcane variety not found")

        stmt = (
            select(Sale)
            .options(selectinload(Sale.customer))
            .where(Sale.sugar_cane_id == variety_id, Sale.deleted_at.is_(None))
            .order_by(Sale.sale_date.desc(), Sale.created_at.desc())
        )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._db.scalar(count_stmt)) or 0

        paginated_stmt = stmt.offset((page - 1) * size).limit(size)
        result = await self._db.execute(paginated_stmt)
        sales = result.scalars().all()

        responses: List[SaleResponse] = []
        for s in sales:
            responses.append(
                SaleResponse(
                    id=s.id,
                    user_id=s.user_id,
                    customer_name=s.customer.name if s.customer else None,
                    sugar_cane_id=s.sugar_cane_id,
                    sugarcane_name=variety.name,
                    unit_type=s.unit_type,
                    quantity=s.quantity,
                    rate=s.rate,
                    total_amount=s.total_amount,
                    sale_date=s.sale_date,
                    notes=s.notes,
                    created_at=s.created_at,
                )
            )

        return responses, total

    async def create_variety(self, payload: SugarCaneCreate) -> SugarCaneResponse:
        existing_name = await self._db.scalar(
            select(SugarCane).where(
                func.lower(SugarCane.name) == payload.name.lower(),
                SugarCane.deleted_at.is_(None),
            )
        )
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Sugarcane variety with name '{payload.name}' already exists",
            )

        if payload.code:
            existing_code = await self._db.scalar(
                select(SugarCane).where(
                    func.upper(SugarCane.code) == payload.code.upper(),
                    SugarCane.deleted_at.is_(None),
                )
            )
            if existing_code:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Sugarcane variety with code '{payload.code}' already exists ({existing_code.name})",
                )

        variety = SugarCane(
            name=payload.name,
            code=payload.code,
            default_rate=payload.default_rate,
            description=payload.description,
            is_active=payload.is_active,
        )
        self._db.add(variety)
        await self._db.commit()
        await self._db.refresh(variety)
        return SugarCaneResponse.model_validate(variety)

    async def update_variety(self, variety_id: UUID, payload: SugarCaneUpdate) -> SugarCaneResponse:
        variety = await self._db.get(SugarCane, variety_id)
        if not variety or variety.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugarcane variety not found")

        update_data = payload.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"]:
            existing_name = await self._db.scalar(
                select(SugarCane).where(
                    func.lower(SugarCane.name) == update_data["name"].lower(),
                    SugarCane.id != variety_id,
                    SugarCane.deleted_at.is_(None),
                )
            )
            if existing_name:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Another sugarcane variety with name '{update_data['name']}' already exists",
                )

        if "code" in update_data and update_data["code"]:
            existing_code = await self._db.scalar(
                select(SugarCane).where(
                    func.upper(SugarCane.code) == update_data["code"].upper(),
                    SugarCane.id != variety_id,
                    SugarCane.deleted_at.is_(None),
                )
            )
            if existing_code:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Another sugarcane variety with code '{update_data['code']}' already exists ({existing_code.name})",
                )

        for key, value in update_data.items():
            setattr(variety, key, value)

        await self._db.commit()
        await self._db.refresh(variety)
        return SugarCaneResponse.model_validate(variety)

    async def delete_variety(self, variety_id: UUID) -> None:
        variety = await self._db.get(SugarCane, variety_id)
        if not variety or variety.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugarcane variety not found")

        sales_count = await self._db.scalar(
            select(func.count(Sale.id)).where(Sale.sugar_cane_id == variety_id, Sale.deleted_at.is_(None))
        ) or 0
        if sales_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete variety '{variety.name}' because {sales_count} sales record(s) are linked to it. Please mark it as inactive instead.",
            )

        variety.deleted_at = func.now()
        await self._db.commit()
