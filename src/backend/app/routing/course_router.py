from fastapi import APIRouter, Depends
from app.services import CourseService
from domain.dto.courses import CourseDto, CourseListingDto, CoursePlanDto, CourseProgressionDto
from .middleware import token_validator, user_id_extractor

router = APIRouter(
    prefix="/courses",
    dependencies=[Depends(token_validator), Depends(user_id_extractor)]
)

@router.get("/", response_model=list[CourseListingDto])
async def get_courses(
    user_id: str = Depends(user_id_extractor), 
    course_service: CourseService = Depends(CourseService)
):
    return await course_service.get_courses(user_id)

@router.get("/{course_id}", response_model=CourseDto)
async def get_course(
    course_id: str,
    user_id: str = Depends(user_id_extractor), 
    course_service: CourseService = Depends(CourseService)
):
    return await course_service.get_course(user_id, course_id)

@router.post("/{course_id}/section-complete", response_model=CourseProgressionDto)
async def complete_section(
    course_id: str,
    user_id: str = Depends(user_id_extractor), 
    course_service: CourseService = Depends(CourseService)
):
    return await course_service.mark_section_as_completed(user_id, course_id)

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
    await course_service.generate_course(user_id, payload)