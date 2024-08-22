from fastapi import APIRouter, Depends, Response
from app.services.instructor_service import InstructorNotFoundError
from app.services import CourseService
from .middleware import token_validator, user_id_extractor
from domain.dto.courses import CoursePlanDto

router = APIRouter(
    prefix="/courses",
    dependencies=[Depends(token_validator), Depends(user_id_extractor)]
)

@router.post("/additional-inputs")
async def get_additional_inputs(
    payload: CoursePlanDto,
    user_id: str = Depends(user_id_extractor), 
    course_service: CourseService = Depends(CourseService)
):
    return await course_service.get_additional_inputs(user_id, payload)
    
@router.post("/generate")
async def generate_course(
    payload: CoursePlanDto,
    user_id: str = Depends(user_id_extractor), 
    course_service: CourseService = Depends(CourseService)
):
    return await course_service.generate_course(user_id, payload)