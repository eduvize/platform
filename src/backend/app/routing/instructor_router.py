from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse
from app.services.instructor_service import InstructorNotFoundError
from domain.dto.instructor.instructor import InstructorDto
from app.services import InstructorService
from .middleware import token_extractor, user_id_extractor

router = APIRouter(
    prefix="/instructor",
    dependencies=[Depends(token_extractor), Depends(user_id_extractor)]
)

@router.get("/", response_model=InstructorDto)
async def get_instructor(
    user_id: str = Depends(user_id_extractor), 
    instructor_service: InstructorService = Depends(InstructorService)
):
    try:
        return await instructor_service.get_instructor(user_id)
    except InstructorNotFoundError:
        return Response(status_code=404)   

@router.get("/generate", response_model=InstructorDto)
async def generate_instructor(
    animal: str, 
    user_id: str = Depends(user_id_extractor), 
    instructor_service: InstructorService = Depends(InstructorService)
):
    # Redirect to the generated avatar URL
    return await instructor_service.generate_instructor(
        user_id=user_id, 
        animal_name=animal
    )