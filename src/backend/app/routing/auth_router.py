from fastapi import APIRouter, Depends
from app.services import AuthService

from .contracts.auth_contracts import AuthenticationPayload, RegistrationPayload, TokenResponse, TokenRefreshPayload

router = APIRouter(prefix="/auth")

@router.post("/login")
async def login(
    payload: AuthenticationPayload, 
    auth_service: AuthService = Depends(AuthService)
):
    access, refresh, expires_in = await auth_service.authenticate(payload.email, payload.password)
    return TokenResponse.model_construct(
        access_token=access, 
        refresh_token=refresh,
        expires_in=expires_in
    )

@router.post("/register")
async def register(
    payload: RegistrationPayload, 
    auth_service: AuthService = Depends(AuthService)
):
    access, refresh, expires_in = await auth_service.register(payload.email, payload.username, payload.password)
    return TokenResponse.model_construct(
        access_token=access, 
        refresh_token=refresh,
        expires_in=expires_in
    )

@router.post("/refresh")
async def refresh(
    payload: TokenRefreshPayload, 
    auth_service: AuthService = Depends(AuthService)
):
    access, refresh, expires_in = await auth_service.refresh_access(payload.refresh_token)
    return TokenResponse.model_construct(
        access_token=access, 
        refresh_token=refresh,
        expires_in=expires_in
    )