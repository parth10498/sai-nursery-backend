import asyncio
from datetime import date
from decimal import Decimal
from sqlalchemy import select, func
from app.db.session import AsyncSessionFactory
from app.models.payment import Payment, PaymentModeEnum
from app.models.sale import Sale
from app.models.sugar_cane import SugarCane
from app.models.user import User, UserTypeEnum


async def seed_customers():
    async with AsyncSessionFactory() as session:
        # Soft-delete or remove any previously created sample customers other than Parth and Jony
        legacy_customers = (
            await session.execute(
                select(User).where(
                    User.type == UserTypeEnum.CUSTOMER,
                    User.name.not_in(["Parth", "Jony"]),
                    User.deleted_at.is_(None),
                )
            )
        ).scalars().all()

        for legacy in legacy_customers:
            legacy.deleted_at = func.now()

        # 1. Fetch available sugarcane varieties for realistic sales allocation
        varieties = (await session.execute(select(SugarCane).where(SugarCane.deleted_at.is_(None)))).scalars().all()
        v_map = {v.code: v for v in varieties}
        v_name_map = {v.name: v for v in varieties}

        def get_variety(code_or_name: str):
            if code_or_name in v_map:
                return v_map[code_or_name]
            if code_or_name in v_name_map:
                return v_name_map[code_or_name]
            return varieties[0] if varieties else None

        v_86032 = get_variety("CO-86032")
        v_0265 = get_variety("COM-0265") or get_variety("PHULE-265")
        v_0238 = get_variety("CO-0238")
        v_15023 = get_variety("CO-15023")
        v_vsi = get_variety("VSI-434")

        # 2. Customer 1: Parth (Active ongoing due with installment history)
        parth_stmt = select(User).where(User.name == "Parth", User.type == UserTypeEnum.CUSTOMER)
        parth = (await session.execute(parth_stmt)).scalar_one_or_none()

        if not parth:
            parth = User(
                name="Parth",
                email="parth@sainursery.com",
                mobile="9822010498",
                type=UserTypeEnum.CUSTOMER,
                address="Plot No. 12, Krishi Nagar, Sangli",
                is_active=True,
            )
            session.add(parth)
            await session.flush()
        else:
            parth.email = "parth@sainursery.com"
            parth.mobile = "9822010498"
            parth.address = "Plot No. 12, Krishi Nagar, Sangli"
            parth.deleted_at = None
            parth.is_active = True

        # 3. Customer 2: Jony (Fully settled dues with complete payment ledger)
        jony_stmt = select(User).where(User.name == "Jony", User.type == UserTypeEnum.CUSTOMER)
        jony = (await session.execute(jony_stmt)).scalar_one_or_none()

        if not jony:
            jony = User(
                name="Jony",
                email="jony@sainursery.com",
                mobile="9822056789",
                type=UserTypeEnum.CUSTOMER,
                address="Survey No. 45, Green Field Road, Navsari",
                is_active=True,
            )
            session.add(jony)
            await session.flush()
        else:
            jony.email = "jony@sainursery.com"
            jony.mobile = "9822056789"
            jony.address = "Survey No. 45, Green Field Road, Navsari"
            jony.deleted_at = None
            jony.is_active = True

        # Check existing sales for Parth and Jony
        existing_parth_sales = (
            await session.execute(select(Sale).where(Sale.user_id == parth.id, Sale.deleted_at.is_(None)))
        ).scalars().all()

        existing_jony_sales = (
            await session.execute(select(Sale).where(Sale.user_id == jony.id, Sale.deleted_at.is_(None)))
        ).scalars().all()

        # 4. Seed Sales for Parth
        # Total Sales: ₹50,000 + ₹32,000 + ₹3,000 = ₹85,000.00
        if not existing_parth_sales:
            parth_sales = [
                Sale(
                    user_id=parth.id,
                    sugar_cane_id=v_86032.id if v_86032 else None,
                    unit_type="QTY",
                    quantity=Decimal("20000.00"),
                    rate=Decimal("2.50"),
                    total_amount=Decimal("50000.00"),
                    sale_date=date(2025, 11, 15),
                    notes="Co 86032 prime seedling batch (Order #PARTH-01)",
                ),
                Sale(
                    user_id=parth.id,
                    sugar_cane_id=v_0238.id if v_0238 else None,
                    unit_type="QTY",
                    quantity=Decimal("10000.00"),
                    rate=Decimal("3.20"),
                    total_amount=Decimal("32000.00"),
                    sale_date=date(2026, 1, 10),
                    notes="Co 0238 (Karan 4) high-sugar cultivar trays (Order #PARTH-02)",
                ),
                Sale(
                    user_id=parth.id,
                    sugar_cane_id=v_vsi.id if v_vsi else None,
                    unit_type="QTY",
                    quantity=Decimal("1000.00"),
                    rate=Decimal("3.00"),
                    total_amount=Decimal("3000.00"),
                    sale_date=date(2026, 1, 20),
                    notes="VSI 434 sample trial seedlings (Order #PARTH-03)",
                ),
            ]
            session.add_all(parth_sales)

        # 5. Seed Payments for Parth
        # Total Payments: ₹30,000 + ₹25,000 = ₹55,000.00
        # Outstanding Due: ₹85,000 - ₹55,000 = ₹30,000.00 pending settlement
        existing_parth_payments = (
            await session.execute(select(Payment).where(Payment.user_id == parth.id, Payment.deleted_at.is_(None)))
        ).scalars().all()

        if not existing_parth_payments:
            parth_payments = [
                Payment(
                    user_id=parth.id,
                    amount_paid=Decimal("30000.00"),
                    payment_date=date(2025, 11, 15),
                    payment_mode=PaymentModeEnum.ONLINE,
                    receipt_no="REC-PARTH-2025-01",
                    notes="Advance token payment via UPI for booking batch #PARTH-01",
                ),
                Payment(
                    user_id=parth.id,
                    amount_paid=Decimal("25000.00"),
                    payment_date=date(2025, 12, 5),
                    payment_mode=PaymentModeEnum.BANK_TRANSFER,
                    receipt_no="REC-PARTH-2025-02",
                    notes="Interim installment paid via NEFT; remaining due balance ₹30,000 scheduled for final delivery",
                ),
            ]
            session.add_all(parth_payments)

        # 6. Seed Sales for Jony
        # Total Sales: ₹75,000 + ₹45,000 = ₹1,20,000.00
        if not existing_jony_sales:
            jony_sales = [
                Sale(
                    user_id=jony.id,
                    sugar_cane_id=v_0265.id if v_0265 else None,
                    unit_type="QTY",
                    quantity=Decimal("25000.00"),
                    rate=Decimal("3.00"),
                    total_amount=Decimal("75000.00"),
                    sale_date=date(2025, 10, 20),
                    notes="CoM 0265 (Phule 265) heavy cane seedlings (Order #JONY-01)",
                ),
                Sale(
                    user_id=jony.id,
                    sugar_cane_id=v_15023.id if v_15023 else None,
                    unit_type="QTY",
                    quantity=Decimal("15000.00"),
                    rate=Decimal("3.00"),
                    total_amount=Decimal("45000.00"),
                    sale_date=date(2025, 12, 10),
                    notes="Co 15023 high recovery early variety dispatch (Order #JONY-02)",
                ),
            ]
            session.add_all(jony_sales)

        # 7. Seed Payments for Jony (Complete Due Settlement)
        # Total Payments: ₹40,000 + ₹50,000 + ₹30,000 = ₹1,20,000.00
        # Outstanding Due: ₹0.00 (Fully Settled)
        existing_jony_payments = (
            await session.execute(select(Payment).where(Payment.user_id == jony.id, Payment.deleted_at.is_(None)))
        ).scalars().all()

        if not existing_jony_payments:
            jony_payments = [
                Payment(
                    user_id=jony.id,
                    amount_paid=Decimal("40000.00"),
                    payment_date=date(2025, 10, 20),
                    payment_mode=PaymentModeEnum.ONLINE,
                    receipt_no="REC-JONY-2025-01",
                    notes="Initial booking token deposit paid online",
                ),
                Payment(
                    user_id=jony.id,
                    amount_paid=Decimal("50000.00"),
                    payment_date=date(2025, 11, 25),
                    payment_mode=PaymentModeEnum.CHEQUE,
                    receipt_no="REC-JONY-2025-02",
                    notes="Second milestone payment paid via Cheque #492011",
                ),
                Payment(
                    user_id=jony.id,
                    amount_paid=Decimal("30000.00"),
                    payment_date=date(2025, 12, 28),
                    payment_mode=PaymentModeEnum.CASH,
                    receipt_no="REC-JONY-2025-03",
                    notes="Final due settlement payment: Full ledger cleared with ₹0 remaining due",
                ),
            ]
            session.add_all(jony_payments)

        await session.commit()
        print("Customer seeder completed successfully!")
        print("Customers seeded: Parth & Jony with sales, payment history, and due settlement details.")


# Backward compatibility alias
seed_customers_and_sales = seed_customers


if __name__ == "__main__":
    asyncio.run(seed_customers())
