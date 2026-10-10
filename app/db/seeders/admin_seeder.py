import asyncio
from passlib.context import CryptContext
from sqlalchemy import select
from app.db.session import AsyncSessionFactory
from app.models.user import User, UserTypeEnum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_admin():
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(User).where(User.email == "nurserysai@yopmail.com")
        )
        existing = result.scalar_one_or_none()
        if existing:
            print("Admin user already exists.")
            return

        admin = User(
            name="Sai Nursery Admin",
            email="nurserysai@yopmail.com",
            password=pwd_context.hash("Admin@123"),
            type=UserTypeEnum.ADMIN,
            mobile="9876543210",
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print("Admin user successfully seeded!")


if __name__ == "__main__":
    asyncio.run(seed_admin())
