import asyncio
from sqlalchemy import select
from app.core.security import get_password_hash
from app.db.session import AsyncSessionFactory
from app.models.user import User, UserTypeEnum


async def seed_admin():
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(User).where(User.email == "nurserysai@yopmail.com")
        )
        existing = result.scalar_one_or_none()
        if existing:
            # Ensure password is refreshed with valid bcrypt hash
            existing.password = get_password_hash("Admin@123")
            existing.is_active = True
            await session.commit()
            print("Admin user updated with fresh password!")
            return

        admin = User(
            name="Sai Nursery Admin",
            email="nurserysai@yopmail.com",
            password=get_password_hash("Admin@123"),
            type=UserTypeEnum.ADMIN,
            mobile="9876543210",
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print("Admin user successfully seeded!")


if __name__ == "__main__":
    asyncio.run(seed_admin())
