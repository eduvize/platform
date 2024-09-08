from fastapi import APIRouter, Depends
from app.routing.middleware import token_validator, user_id_extractor
from app.services import ValidationService
from domain.dto.ai.assertion_result import AssertionResultDto

router = APIRouter(
    prefix="/validation",
    dependencies=[
        Depends(token_validator),
        Depends(user_id_extractor)
    ]
)

@router.get("/assert", response_model=AssertionResultDto)
async def assert_validation(
    query: str, 
    validation_service: ValidationService = Depends(ValidationService)
):
    return await validation_service.perform_assertion(query)