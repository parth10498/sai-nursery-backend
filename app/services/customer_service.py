from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.geo import City, Country, State
from app.models.payment import Payment
from app.models.sale import Sale
from app.models.user import User, UserTypeEnum
from app.schemas.customer import CustomerCreate, CustomerLedgerResponse, CustomerResponse, CustomerUpdate


class CustomerService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_customer_totals(self, customer_id: UUID) -> Tuple[Decimal, Decimal, Decimal]:
        total_sales = await self._db.scalar(
            select(func.coalesce(func.sum(Sale.total_amount), 0)).where(
                Sale.user_id == customer_id,
                Sale.deleted_at.is_(None),
            )
        ) or Decimal("0.00")

        total_paid = await self._db.scalar(
            select(func.coalesce(func.sum(Payment.amount_paid), 0)).where(
                Payment.user_id == customer_id,
                Payment.deleted_at.is_(None),
            )
        ) or Decimal("0.00")

        balance = total_sales - total_paid
        return Decimal(str(total_sales)), Decimal(str(total_paid)), Decimal(str(balance))

    async def list_customers(
        self,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[CustomerResponse], int]:
        stmt = (
            select(User)
            .where(
                User.type == UserTypeEnum.CUSTOMER,
                User.deleted_at.is_(None),
            )
            .order_by(User.name.asc())
        )

        if search:
            search_pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                (User.name.ilike(search_pattern))
                | (User.mobile.ilike(search_pattern))
                | (User.email.ilike(search_pattern))
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._db.scalar(count_stmt)) or 0

        paginated_stmt = stmt.offset((page - 1) * size).limit(size)
        result = await self._db.execute(paginated_stmt)
        users = result.scalars().all()

        responses: List[CustomerResponse] = []
        for u in users:
            sales_sum, paid_sum, bal = await self.get_customer_totals(u.id)
            c_resp = CustomerResponse(
                id=u.id,
                name=u.name,
                email=u.email,
                mobile=u.mobile,
                address=u.address,
                country_id=u.country_id,
                state_id=u.state_id,
                city_id=u.city_id,
                state_name=u.state.name if u.state else None,
                city_name=u.city.name if u.city else None,
                pincode=u.pincode,
                is_active=u.is_active,
                total_sales=sales_sum,
                total_paid=paid_sum,
                balance=bal,
                created_at=u.created_at,
            )
            responses.append(c_resp)

        return responses, total

    async def _validate_location(
        self, country_id: Optional[int], state_id: Optional[int], city_id: Optional[int]
    ) -> None:
        if country_id:
            c = await self._db.get(Country, country_id)
            if not c:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Country with ID {country_id} does not exist")
        if state_id:
            s = await self._db.get(State, state_id)
            if not s:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"State with ID {state_id} does not exist")
        if city_id:
            ct = await self._db.get(City, city_id)
            if not ct:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"City/Taluka with ID {city_id} does not exist")

    async def create_customer(self, payload: CustomerCreate) -> CustomerResponse:
        # Check duplicate mobile
        if payload.mobile:
            existing_mobile = await self._db.scalar(
                select(User).where(
                    User.mobile == payload.mobile,
                    User.type == UserTypeEnum.CUSTOMER,
                    User.deleted_at.is_(None),
                )
            )
            if existing_mobile:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Customer with mobile number '{payload.mobile}' already exists ({existing_mobile.name})",
                )

        # Check duplicate email
        if payload.email:
            existing_email = await self._db.scalar(
                select(User).where(
                    User.email == payload.email,
                    User.type == UserTypeEnum.CUSTOMER,
                    User.deleted_at.is_(None),
                )
            )
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Customer with email '{payload.email}' already exists ({existing_email.name})",
                )

        # Validate locations if provided
        await self._validate_location(payload.country_id, payload.state_id, payload.city_id)

        user = User(
            name=payload.name,
            email=payload.email,
            mobile=payload.mobile,
            address=payload.address,
            country_id=payload.country_id,
            state_id=payload.state_id,
            city_id=payload.city_id,
            pincode=payload.pincode,
            is_active=payload.is_active,
            type=UserTypeEnum.CUSTOMER,
        )
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)

        return CustomerResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            mobile=user.mobile,
            address=user.address,
            country_id=user.country_id,
            state_id=user.state_id,
            city_id=user.city_id,
            state_name=user.state.name if user.state else None,
            city_name=user.city.name if user.city else None,
            pincode=user.pincode,
            is_active=user.is_active,
            total_sales=Decimal("0.00"),
            total_paid=Decimal("0.00"),
            balance=Decimal("0.00"),
            created_at=user.created_at,
        )

    async def get_customer(self, customer_id: UUID) -> CustomerResponse:
        user = await self._db.get(User, customer_id)
        if not user or user.deleted_at is not None or user.type != UserTypeEnum.CUSTOMER:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        sales_sum, paid_sum, bal = await self.get_customer_totals(user.id)
        return CustomerResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            mobile=user.mobile,
            address=user.address,
            country_id=user.country_id,
            state_id=user.state_id,
            city_id=user.city_id,
            state_name=user.state.name if user.state else None,
            city_name=user.city.name if user.city else None,
            pincode=user.pincode,
            is_active=user.is_active,
            total_sales=sales_sum,
            total_paid=paid_sum,
            balance=bal,
            created_at=user.created_at,
        )

    async def update_customer(self, customer_id: UUID, payload: CustomerUpdate) -> CustomerResponse:
        user = await self._db.get(User, customer_id)
        if not user or user.deleted_at is not None or user.type != UserTypeEnum.CUSTOMER:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        update_data = payload.model_dump(exclude_unset=True)

        # Check duplicate mobile excluding self
        if "mobile" in update_data and update_data["mobile"]:
            existing_mobile = await self._db.scalar(
                select(User).where(
                    User.mobile == update_data["mobile"],
                    User.id != customer_id,
                    User.type == UserTypeEnum.CUSTOMER,
                    User.deleted_at.is_(None),
                )
            )
            if existing_mobile:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Another customer with mobile number '{update_data['mobile']}' already exists ({existing_mobile.name})",
                )

        # Check duplicate email excluding self
        if "email" in update_data and update_data["email"]:
            existing_email = await self._db.scalar(
                select(User).where(
                    User.email == update_data["email"],
                    User.id != customer_id,
                    User.type == UserTypeEnum.CUSTOMER,
                    User.deleted_at.is_(None),
                )
            )
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Another customer with email '{update_data['email']}' already exists ({existing_email.name})",
                )

        # Validate location if updated
        await self._validate_location(
            update_data.get("country_id"),
            update_data.get("state_id"),
            update_data.get("city_id"),
        )

        for key, value in update_data.items():
            setattr(user, key, value)

        await self._db.commit()
        await self._db.refresh(user)
        return await self.get_customer(customer_id)

    async def delete_customer(self, customer_id: UUID) -> None:
        user = await self._db.get(User, customer_id)
        if not user or user.deleted_at is not None or user.type != UserTypeEnum.CUSTOMER:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        user.deleted_at = func.now()
        await self._db.commit()

    async def get_ledger(self, customer_id: UUID) -> CustomerLedgerResponse:
        user = await self._db.get(User, customer_id)
        if not user or user.deleted_at is not None or user.type != UserTypeEnum.CUSTOMER:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        sales_count = await self._db.scalar(
            select(func.count(Sale.id)).where(Sale.user_id == customer_id, Sale.deleted_at.is_(None))
        ) or 0

        payments_count = await self._db.scalar(
            select(func.count(Payment.id)).where(Payment.user_id == customer_id, Payment.deleted_at.is_(None))
        ) or 0

        sales_sum, paid_sum, bal = await self.get_customer_totals(customer_id)

        return CustomerLedgerResponse(
            customer_id=user.id,
            customer_name=user.name,
            total_sales=sales_sum,
            total_paid=paid_sum,
            balance=bal,
            sales_count=sales_count,
            payments_count=payments_count,
        )
