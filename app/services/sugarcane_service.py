from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sale import Sale
from app.models.sugar_cane import SugarCane
from app.schemas.sugar_cane import SugarCaneCreate, SugarCaneResponse, SugarCaneUpdate


class SugarCaneService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def list_varieties(self, active_only: bool = False) -> List[SugarCaneResponse]:
        stmt = select(SugarCane).where(SugarCane.deleted_at.is_(None)).order_by(SugarCane.name.asc())
        if active_only:
            stmt = stmt.where(SugarCane.is_active.is_(True))

        result = await self._db.execute(stmt)
        varieties = result.scalars().all()
        return [SugarCaneResponse.model_validate(v) for v in varieties]

    async def get_variety(self, variety_id: UUID) -> SugarCaneResponse:
        variety = await self._db.get(SugarCane, variety_id)
        if not variety or variety.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugarcane variety not found")
        return SugarCaneResponse.model_validate(variety)

    async def create_variety(self, payload: SugarCaneCreate) -> SugarCaneResponse:
        # Check duplicate name
        existing_name = await self._db.scalar(
            select(SugarCane).where(
                func.lower(SugarCane.name) == payload.name.lower(),
                SugarCane.deleted_at.is_(None),
            )
        )
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Sugarcane variety with name '{payload.name}' already exists",
            )

        # Check duplicate code if code provided
        if payload.code:
            existing_code = await self._db.scalar(
                select(SugarCane).where(
                    func.upper(SugarCane.code) == payload.code.upper(),
                    SugarCane.deleted_at.is_(None),
                )
            )
            if existing_code:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Sugarcane variety with code '{payload.code}' already exists ({existing_code.name})",
                )

        variety = SugarCane(
            name=payload.name,
            code=payload.code,
            default_rate=payload.default_rate,
            description=payload.description,
            is_active=payload.is_active,
        )
        self._db.add(variety)
        await self._db.commit()
        await self._db.refresh(variety)
        return SugarCaneResponse.model_validate(variety)

    async def update_variety(self, variety_id: UUID, payload: SugarCaneUpdate) -> SugarCaneResponse:
        variety = await self._db.get(SugarCane, variety_id)
        if not variety or variety.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugarcane variety not found")

        update_data = payload.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"]:
            existing_name = await self._db.scalar(
                select(SugarCane).where(
                    func.lower(SugarCane.name) == update_data["name"].lower(),
                    SugarCane.id != variety_id,
                    SugarCane.deleted_at.is_(None),
                )
            )
            if existing_name:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Another sugarcane variety with name '{update_data['name']}' already exists",
                )

        if "code" in update_data and update_data["code"]:
            existing_code = await self._db.scalar(
                select(SugarCane).where(
                    func.upper(SugarCane.code) == update_data["code"].upper(),
                    SugarCane.id != variety_id,
                    SugarCane.deleted_at.is_(None),
                )
            )
            if existing_code:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Another sugarcane variety with code '{update_data['code']}' already exists ({existing_code.name})",
                )

        for key, value in update_data.items():
            setattr(variety, key, value)

        await self._db.commit()
        await self._db.refresh(variety)
        return SugarCaneResponse.model_validate(variety)

    async def delete_variety(self, variety_id: UUID) -> None:
        variety = await self._db.get(SugarCane, variety_id)
        if not variety or variety.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugarcane variety not found")

        sales_count = await self._db.scalar(
            select(func.count(Sale.id)).where(Sale.sugar_cane_id == variety_id, Sale.deleted_at.is_(None))
        ) or 0
        if sales_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete variety '{variety.name}' because {sales_count} sales record(s) are linked to it. Please mark it as inactive instead.",
            )

        variety.deleted_at = func.now()
        await self._db.commit()
