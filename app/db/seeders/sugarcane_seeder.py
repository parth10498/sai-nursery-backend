import asyncio
from decimal import Decimal
from sqlalchemy import select
from app.db.session import AsyncSessionFactory
from app.models.sugar_cane import SugarCane


async def seed_sugarcane():
    async with AsyncSessionFactory() as session:
        varieties = [
            {"name": "Co 86032 (Nira)", "code": "CO-86032", "default_rate": Decimal("2.50")},
            {"name": "CoM 0265 (Phule 265)", "code": "COM-0265", "default_rate": Decimal("3.00")},
            {"name": "MS 10001", "code": "MS-10001", "default_rate": Decimal("3.50")},
            {"name": "Co 92005", "code": "CO-92005", "default_rate": Decimal("2.80")},
        ]

        for item in varieties:
            res = await session.execute(
                select(SugarCane).where(SugarCane.name == item["name"])
            )
            if not res.scalar_one_or_none():
                sc = SugarCane(
                    name=item["name"],
                    code=item["code"],
                    default_rate=item["default_rate"],
                    is_active=True,
                )
                session.add(sc)

        await session.commit()
        print("Sugarcane varieties seeded!")


if __name__ == "__main__":
    asyncio.run(seed_sugarcane())
