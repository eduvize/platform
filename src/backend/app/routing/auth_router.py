from typing import Optional
from fastapi import APIRouter, Depends, Response
from app.services import AuthService
from .middleware.token_middleware import get_access_token

from .contracts.auth_contracts import AuthenticationPayload, RegistrationPayload, TokenResponse, RefreshTokenPayload

router = APIRouter(
    prefix="/auth"
)

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
    payload: RefreshTokenPayload, 
    auth_service: AuthService = Depends(AuthService)
):
    access, refresh, expires_in = await auth_service.refresh_access(payload.refresh_token)
    return TokenResponse.model_construct(
        access_token=access, 
        refresh_token=refresh,
        expires_in=expires_in
    )
    
@router.delete("/")
async def logout(
    payload: RefreshTokenPayload,
    access_token: Optional[str] = Depends(get_access_token),
    auth_service: AuthService = Depends(AuthService),
):
    auth_service.logout(
        access_token=access_token, 
        refresh_token=payload.refresh_token
    )
    
    return Response(status_code=200)