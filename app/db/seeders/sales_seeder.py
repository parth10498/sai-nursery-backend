import asyncio
from app.db.seeders.customer_seeder import seed_customers, seed_customers_and_sales


if __name__ == "__main__":
    asyncio.run(seed_customers())
