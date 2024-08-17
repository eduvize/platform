from fastapi import APIRouter, Depends, Response
from fastapi.security import HTTPBasicCredentials
from app.services import PlaygroundService
from .middleware import basic_authorization
from .contracts.playground_contracts import PlaygroundHostnamePayload, PlaygroundSessionResponse, PlaygroundFinalizerPayload

router = APIRouter(
    prefix="/playground",
)

@router.post("/")
async def create_playground_instance(
    playground_service: PlaygroundService = Depends(PlaygroundService)
):
    await playground_service.create_playground()
    
@router.post("/internal/reservations")
async def create_reservation(
    payload: PlaygroundHostnamePayload,
    playground_service: PlaygroundService = Depends(PlaygroundService),
    credentials: HTTPBasicCredentials = Depends(basic_authorization)
):
    reservation = await playground_service.create_reservation(payload.hostname)
    
    if not reservation:
        return Response(status_code=404)
    
    session_id, session_type = reservation
    print(f"Response: {session_id}, {session_type}")
    
    return PlaygroundSessionResponse.model_construct(
        session_id=session_id,
        session_type=session_type
    )

@router.get("/internal/reservations/{hostname}")
async def validate_reservation(
    hostname: str,
    playground_service: PlaygroundService = Depends(PlaygroundService),
    credentials: HTTPBasicCredentials = Depends(basic_authorization)
):
    is_available = await playground_service.validate_reservation(hostname)
    
    if not is_available:
        return Response(status_code=404)
    
    return Response(status_code=200)

@router.delete("/internal/session")
async def kill_pod(
    payload: PlaygroundFinalizerPayload,
    playground_service: PlaygroundService = Depends(PlaygroundService),
    credentials: HTTPBasicCredentials = Depends(basic_authorization)
):
    print(f"Instance {payload.hostname} is being terminated")