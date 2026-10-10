from typing import List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment
from app.models.user import User, UserTypeEnum
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate


class PaymentService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def list_payments(
        self,
        customer_id: Optional[UUID] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[PaymentResponse], int]:
        stmt = (
            select(Payment)
            .options(selectinload(Payment.customer))
            .where(Payment.deleted_at.is_(None))
            .order_by(Payment.payment_date.desc(), Payment.created_at.desc())
        )
        if customer_id:
            stmt = stmt.where(Payment.user_id == customer_id)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._db.scalar(count_stmt)) or 0

        paginated_stmt = stmt.offset((page - 1) * size).limit(size)
        result = await self._db.execute(paginated_stmt)
        payments = result.scalars().all()

        responses: List[PaymentResponse] = []
        for p in payments:
            responses.append(
                PaymentResponse(
                    id=p.id,
                    user_id=p.user_id,
                    customer_name=p.customer.name if p.customer else None,
                    amount_paid=p.amount_paid,
                    payment_date=p.payment_date,
                    payment_mode=p.payment_mode,
                    receipt_no=p.receipt_no,
                    payment_proof_url=p.payment_proof_url,
                    notes=p.notes,
                    created_at=p.created_at,
                )
            )

        return responses, total

    async def get_payment(self, payment_id: UUID) -> PaymentResponse:
        stmt = (
            select(Payment)
            .options(selectinload(Payment.customer))
            .where(Payment.id == payment_id, Payment.deleted_at.is_(None))
        )
        payment = (await self._db.execute(stmt)).scalar_one_or_none()
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")

        return PaymentResponse(
            id=payment.id,
            user_id=payment.user_id,
            customer_name=payment.customer.name if payment.customer else None,
            amount_paid=payment.amount_paid,
            payment_date=payment.payment_date,
            payment_mode=payment.payment_mode,
            receipt_no=payment.receipt_no,
            payment_proof_url=payment.payment_proof_url,
            notes=payment.notes,
            created_at=payment.created_at,
        )

    async def create_payment(self, payload: PaymentCreate) -> PaymentResponse:
        customer = await self._db.get(User, payload.user_id)
        if not customer or customer.deleted_at is not None or customer.type != UserTypeEnum.CUSTOMER:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        payment = Payment(
            user_id=payload.user_id,
            amount_paid=payload.amount_paid,
            payment_date=payload.payment_date,
            payment_mode=payload.payment_mode,
            receipt_no=payload.receipt_no,
            payment_proof_url=payload.payment_proof_url,
            notes=payload.notes,
        )
        self._db.add(payment)
        await self._db.commit()
        await self._db.refresh(payment)

        return PaymentResponse(
            id=payment.id,
            user_id=payment.user_id,
            customer_name=customer.name,
            amount_paid=payment.amount_paid,
            payment_date=payment.payment_date,
            payment_mode=payment.payment_mode,
            receipt_no=payment.receipt_no,
            payment_proof_url=payment.payment_proof_url,
            notes=payment.notes,
            created_at=payment.created_at,
        )

    async def update_payment(self, payment_id: UUID, payload: PaymentUpdate) -> PaymentResponse:
        payment = await self._db.get(Payment, payment_id)
        if not payment or payment.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(payment, key, value)

        await self._db.commit()
        await self._db.refresh(payment)
        return await self.get_payment(payment_id)

    async def delete_payment(self, payment_id: UUID) -> None:
        payment = await self._db.get(Payment, payment_id)
        if not payment or payment.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")

        payment.deleted_at = func.now()
        await self._db.commit()
