from fastapi import APIRouter, Depends

from .contracts.auth_contracts import AuthenticationPayload, RegistrationPayload, TokenResponse
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth")

@router.post("/login")
async def login(payload: AuthenticationPayload, auth_service: AuthService = Depends(AuthService)):
    token = await auth_service.authenticate(payload.email, payload.password)
    return TokenResponse.model_construct(token=token)

@router.post("/register")
async def register(payload: RegistrationPayload, auth_service: AuthService = Depends(AuthService)):
    token = await auth_service.register(payload.email, payload.username, payload.password)
    return TokenResponse.model_construct(token=token)