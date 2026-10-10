from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import CurrentUser, DBSession
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.base import ApiResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
):
    service = AuthService(db)
    return await service.authenticate(
        LoginRequest(username=form_data.username, password=form_data.password)
    )


@router.post("/login/json", response_model=ApiResponse[TokenResponse])
async def login_json(payload: LoginRequest, db: DBSession):
    service = AuthService(db)
    token = await service.authenticate(payload)
    return ApiResponse(data=token, message="Login successful")


@router.get("/me")
async def get_me(user: CurrentUser):
    return ApiResponse(
        data={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile,
            "type": user.type.value,
        }
    )
