import asyncio
from app.db.seeders.admin_seeder import seed_admin
from app.db.seeders.geo_seeder import seed_geo
from app.db.seeders.sugarcane_seeder import seed_sugarcane
from app.db.seeders.customer_seeder import seed_customers


async def init_db():
    print("Starting database seeding...")
    await seed_geo()
    await seed_admin()
    await seed_sugarcane()
    await seed_customers()
    print("All initial seeders completed successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
