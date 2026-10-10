from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def authenticate(self, payload: LoginRequest) -> TokenResponse:
        stmt = (
            select(User)
            .where(
                (User.email == payload.username) | (User.mobile == payload.username),
                User.deleted_at.is_(None),
            )
        )
        result = await self._db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        if not verify_password(payload.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Contact administrator.",
            )

        token = create_access_token(
            data={"sub": str(user.id), "role": user.type.value, "name": user.name}
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            name=user.name,
            email=user.email,
            role=user.type.value,
        )
