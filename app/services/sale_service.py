from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sale import Sale
from app.models.sugar_cane import SugarCane
from app.models.user import User, UserTypeEnum
from app.schemas.sale import SaleCreate, SaleResponse, SaleUpdate


class SaleService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def list_sales(
        self,
        customer_id: Optional[UUID] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[SaleResponse], int]:
        stmt = select(Sale).where(Sale.deleted_at.is_(None)).order_by(Sale.sale_date.desc(), Sale.created_at.desc())
        if customer_id:
            stmt = stmt.where(Sale.user_id == customer_id)

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
                    sugarcane_name=s.sugarcane.name if s.sugarcane else None,
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

    async def get_sale(self, sale_id: UUID) -> SaleResponse:
        sale = await self._db.get(Sale, sale_id)
        if not sale or sale.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

        return SaleResponse(
            id=sale.id,
            user_id=sale.user_id,
            customer_name=sale.customer.name if sale.customer else None,
            sugar_cane_id=sale.sugar_cane_id,
            sugarcane_name=sale.sugarcane.name if sale.sugarcane else None,
            unit_type=sale.unit_type,
            quantity=sale.quantity,
            rate=sale.rate,
            total_amount=sale.total_amount,
            sale_date=sale.sale_date,
            notes=sale.notes,
            created_at=sale.created_at,
        )

    async def create_sale(self, payload: SaleCreate) -> SaleResponse:
        # Verify customer exists
        customer = await self._db.get(User, payload.user_id)
        if not customer or customer.deleted_at is not None or customer.type != UserTypeEnum.CUSTOMER:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        # Verify variety if provided
        sc = None
        if payload.sugar_cane_id:
            sc = await self._db.get(SugarCane, payload.sugar_cane_id)
            if not sc or sc.deleted_at is not None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugarcane variety not found")

        # Compute total_amount server-side
        total = (payload.quantity * payload.rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        sale = Sale(
            user_id=payload.user_id,
            sugar_cane_id=payload.sugar_cane_id,
            unit_type=payload.unit_type,
            quantity=payload.quantity,
            rate=payload.rate,
            total_amount=total,
            sale_date=payload.sale_date,
            notes=payload.notes,
        )
        self._db.add(sale)
        await self._db.commit()
        await self._db.refresh(sale)

        return SaleResponse(
            id=sale.id,
            user_id=sale.user_id,
            customer_name=customer.name,
            sugar_cane_id=sale.sugar_cane_id,
            sugarcane_name=sc.name if sc else None,
            unit_type=sale.unit_type,
            quantity=sale.quantity,
            rate=sale.rate,
            total_amount=sale.total_amount,
            sale_date=sale.sale_date,
            notes=sale.notes,
            created_at=sale.created_at,
        )

    async def update_sale(self, sale_id: UUID, payload: SaleUpdate) -> SaleResponse:
        sale = await self._db.get(Sale, sale_id)
        if not sale or sale.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

        update_data = payload.model_dump(exclude_unset=True)

        if "sugar_cane_id" in update_data and update_data["sugar_cane_id"]:
            sc = await self._db.get(SugarCane, update_data["sugar_cane_id"])
            if not sc or sc.deleted_at is not None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugarcane variety not found")

        for key, value in update_data.items():
            setattr(sale, key, value)

        # Recalculate total_amount server-side
        total = (sale.quantity * sale.rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        sale.total_amount = total

        await self._db.commit()
        await self._db.refresh(sale)
        return await self.get_sale(sale_id)

    async def delete_sale(self, sale_id: UUID) -> None:
        sale = await self._db.get(Sale, sale_id)
        if not sale or sale.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

        sale.deleted_at = func.now()
        await self._db.commit()
