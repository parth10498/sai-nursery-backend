import asyncio
from datetime import date
from decimal import Decimal
from sqlalchemy import select
from app.db.session import AsyncSessionFactory
from app.models.sale import Sale
from app.models.sugar_cane import SugarCane
from app.models.user import User, UserTypeEnum


async def seed_customers_and_sales():
    async with AsyncSessionFactory() as session:
        # 1. Ensure Customers exist
        customers_data = [
            {"name": "Ramesh Baburao Patil", "email": "ramesh.patil@agrimail.com", "mobile": "9822012345"},
            {"name": "Suresh Dattatray Shinde", "email": "suresh.shinde@agrimail.com", "mobile": "9822054321"},
            {"name": "Vikas Anandrao Deshmukh", "email": "vikas.deshmukh@agrimail.com", "mobile": "9822098765"},
        ]

        customer_map = {}
        for c in customers_data:
            stmt = select(User).where(User.mobile == c["mobile"])
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if not existing:
                u = User(
                    name=c["name"],
                    email=c["email"],
                    mobile=c["mobile"],
                    type=UserTypeEnum.CUSTOMER,
                    is_active=True,
                )
                session.add(u)
                await session.flush()
                customer_map[c["name"]] = u
            else:
                customer_map[c["name"]] = existing

        # 2. Get Sugarcane varieties
        varieties = (await session.execute(select(SugarCane))).scalars().all()
        v_map = {v.name: v for v in varieties}

        if not v_map:
            print("No sugarcane varieties found. Run sugarcane_seeder first.")
            return

        c1 = customer_map["Ramesh Baburao Patil"]
        c2 = customer_map["Suresh Dattatray Shinde"]
        c3 = customer_map["Vikas Anandrao Deshmukh"]

        v_nira = v_map.get("Co 86032 (Nira)") or varieties[0]
        v_phule = v_map.get("CoM 0265 (Phule 265)") or varieties[min(1, len(varieties) - 1)]
        v_ms = v_map.get("MS 10001") or varieties[min(2, len(varieties) - 1)]
        v_92005 = v_map.get("Co 92005") or varieties[min(3, len(varieties) - 1)]

        # Check existing sales count
        existing_sales_count = (
            await session.execute(select(Sale).where(Sale.deleted_at.is_(None)))
        ).scalars().all()

        if len(existing_sales_count) >= 10:
            print(f"Sales already seeded ({len(existing_sales_count)} records present).")
            return

        # Seed realistic sales across Kharif-Rabi season
        # QTY sales (Plants): Oct(18k), Nov(28k), Dec(42k), Jan(35k), Feb(22k) = 145,000 Plants
        # TONS sales (Weight): Oct(45T), Nov(82T), Dec(130T), Jan(125T), Feb(103.5T) = 485.50 Tons
        sales_records = [
            # October 2025
            Sale(
                user_id=c1.id,
                sugar_cane_id=v_nira.id,
                unit_type="QTY",
                quantity=Decimal("18000.00"),
                rate=Decimal("2.50"),
                total_amount=Decimal("45000.00"),
                sale_date=date(2025, 10, 15),
                notes="Nursery seedling batch 1",
            ),
            Sale(
                user_id=c2.id,
                sugar_cane_id=v_nira.id,
                unit_type="TONS",
                quantity=Decimal("45.00"),
                rate=Decimal("3200.00"),
                total_amount=Decimal("144000.00"),
                sale_date=date(2025, 10, 24),
                notes="Early season mill supply dispatch",
            ),
            # November 2025
            Sale(
                user_id=c2.id,
                sugar_cane_id=v_phule.id,
                unit_type="QTY",
                quantity=Decimal("28000.00"),
                rate=Decimal("3.00"),
                total_amount=Decimal("84000.00"),
                sale_date=date(2025, 11, 10),
                notes="Phule 265 seedling trays",
            ),
            Sale(
                user_id=c3.id,
                sugar_cane_id=v_phule.id,
                unit_type="TONS",
                quantity=Decimal("82.00"),
                rate=Decimal("3500.00"),
                total_amount=Decimal("287000.00"),
                sale_date=date(2025, 11, 22),
                notes="Phule 265 heavy stalk harvest",
            ),
            # December 2025 (Peak Harvest Month)
            Sale(
                user_id=c1.id,
                sugar_cane_id=v_nira.id,
                unit_type="QTY",
                quantity=Decimal("42000.00"),
                rate=Decimal("2.50"),
                total_amount=Decimal("105000.00"),
                sale_date=date(2025, 12, 12),
                notes="Peak season primary nursery dispatch",
            ),
            Sale(
                user_id=c1.id,
                sugar_cane_id=v_nira.id,
                unit_type="TONS",
                quantity=Decimal("130.00"),
                rate=Decimal("3200.00"),
                total_amount=Decimal("416000.00"),
                sale_date=date(2025, 12, 28),
                notes="Co 86032 main cut sugar factory delivery",
            ),
            # January 2026
            Sale(
                user_id=c3.id,
                sugar_cane_id=v_ms.id,
                unit_type="QTY",
                quantity=Decimal("35000.00"),
                rate=Decimal("3.50"),
                total_amount=Decimal("122500.00"),
                sale_date=date(2026, 1, 14),
                notes="High brix tissue culture plants",
            ),
            Sale(
                user_id=c2.id,
                sugar_cane_id=v_phule.id,
                unit_type="TONS",
                quantity=Decimal("125.00"),
                rate=Decimal("3500.00"),
                total_amount=Decimal("437500.00"),
                sale_date=date(2026, 1, 26),
                notes="Bulk cane harvest dispatch",
            ),
            # February 2026
            Sale(
                user_id=c1.id,
                sugar_cane_id=v_92005.id,
                unit_type="QTY",
                quantity=Decimal("22000.00"),
                rate=Decimal("2.80"),
                total_amount=Decimal("61600.00"),
                sale_date=date(2026, 2, 8),
                notes="Co 92005 certified seedlings",
            ),
            Sale(
                user_id=c3.id,
                sugar_cane_id=v_ms.id,
                unit_type="TONS",
                quantity=Decimal("103.50"),
                rate=Decimal("3800.00"),
                total_amount=Decimal("393300.00"),
                sale_date=date(2026, 2, 20),
                notes="MS 10001 high brix crushing tonnage",
            ),
        ]

        session.add_all(sales_records)
        await session.commit()
        print(f"Successfully seeded {len(sales_records)} realistic sales records!")


if __name__ == "__main__":
    asyncio.run(seed_customers_and_sales())
