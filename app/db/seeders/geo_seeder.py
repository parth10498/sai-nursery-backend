import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionFactory
from app.models.geo import Country, State, City


async def seed_geo():
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(Country).where(Country.name == "India"))
        country = result.scalar_one_or_none()
        if not country:
            country = Country(name="India", code="IN")
            session.add(country)
            await session.flush()

        result = await session.execute(
            select(State).where(State.name == "Maharashtra", State.country_id == country.id)
        )
        state = result.scalar_one_or_none()
        if not state:
            state = State(name="Maharashtra", country_id=country.id)
            session.add(state)
            await session.flush()

        cities_data = ["Pune", "Satara", "Kolhapur", "Sangli", "Solapur", "Ahmednagar"]
        for city_name in cities_data:
            c_result = await session.execute(
                select(City).where(City.name == city_name, City.state_id == state.id)
            )
            if not c_result.scalar_one_or_none():
                session.add(City(name=city_name, state_id=state.id))

        await session.commit()
        print("Geo reference data seeded!")


if __name__ == "__main__":
    asyncio.run(seed_geo())
