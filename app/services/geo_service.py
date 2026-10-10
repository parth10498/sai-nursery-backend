from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.geo import City, Country, State


class GeoService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_countries(self) -> List[Country]:
        result = await self._db.execute(select(Country).order_by(Country.name.asc()))
        return list(result.scalars().all())

    async def get_states(self, country_id: int) -> List[State]:
        result = await self._db.execute(
            select(State).where(State.country_id == country_id).order_by(State.name.asc())
        )
        return list(result.scalars().all())

    async def get_cities(self, state_id: int) -> List[City]:
        result = await self._db.execute(
            select(City).where(City.state_id == state_id).order_by(City.name.asc())
        )
        return list(result.scalars().all())
