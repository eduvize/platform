from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from domain.dto.instructor.instructor import InstructorDto
from app.services import InstructorService
from .middleware import token_extractor, user_id_extractor

router = APIRouter(
    prefix="/instructor",
    dependencies=[Depends(token_extractor), Depends(user_id_extractor)]
)

@router.get("/generate", response_model=InstructorDto)
async def generate_instructor(animal: str, instructor_service: InstructorService = Depends(InstructorService)):
    # Redirect to the generated avatar URL
    return await instructor_service.generate_instructor(animal)