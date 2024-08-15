from fastapi import APIRouter, Depends
from app.routing.middleware import token_extractor, user_id_extractor
from app.services import ValidationService
from .contracts import AssertionResult

router = APIRouter(
    prefix="/validation",
    dependencies=[
        Depends(token_extractor),
        Depends(user_id_extractor)
    ]
)

@router.get("/assert", response_model=AssertionResult)
async def assert_validation(
    query: str, 
    validation_service: ValidationService = Depends(ValidationService)
):
    return await validation_service.perform_assertion(query)