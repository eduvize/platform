import uuid
from fastapi import APIRouter, Depends
from app.services import CourseService
from domain.dto.courses import CourseDto, CourseListingDto, CoursePlanDto, CourseProgressionDto, InternalExerciseDto
from .middleware import user_id_extractor, playground_token_validator
from common.messaging import KafkaProducer, Topic
from domain.topics import CourseGeneratedTopic

router = APIRouter(
    prefix="/courses"
)

@router.get("/", response_model=list[CourseListingDto], dependencies=[Depends(user_id_extractor)])
async def get_courses(
    user_id: str = Depends(user_id_extractor), 
    course_service: CourseService = Depends(CourseService)
):
    return await course_service.get_courses(user_id)

@router.get("/{course_id}", response_model=CourseDto, dependencies=[Depends(user_id_extractor)])
async def get_course(
    course_id: str,
    user_id: str = Depends(user_id_extractor), 
    course_service: CourseService = Depends(CourseService)
):
    return await course_service.get_course(user_id, course_id)

@router.get("/internal/exercises/{exercise_id}", response_model=InternalExerciseDto, dependencies=[Depends(playground_token_validator)])
async def get_course_internal(
    exercise_id: uuid.UUID,
    course_service: CourseService = Depends(CourseService),
):
    return await course_service.get_exercise(exercise_id)

@router.post("/internal/exercises/{exercise_id}/objectives/{objective_id}/complete", dependencies=[Depends(playground_token_validator)])
async def complete_objective_internal(
    exercise_id: uuid.UUID,
    objective_id: uuid.UUID,
    course_service: CourseService = Depends(CourseService)
):
    return await course_service.complete_objective(exercise_id, objective_id)

@router.post("/{course_id}/section-complete", response_model=CourseProgressionDto, dependencies=[Depends(user_id_extractor)])
async def complete_section(
    course_id: str,
    user_id: str = Depends(user_id_extractor), 
    course_service: CourseService = Depends(CourseService)
):
    return await course_service.mark_section_as_completed(user_id, course_id)

@router.post("/additional-inputs", dependencies=[Depends(user_id_extractor)])
async def get_additional_inputs(
    payload: CoursePlanDto,
    user_id: str = Depends(user_id_extractor), 
    course_service: CourseService = Depends(CourseService)
):
    return await course_service.get_additional_inputs(user_id, payload)
    
@router.post("/generate", dependencies=[Depends(user_id_extractor)])
async def generate_course(
    payload: CoursePlanDto,
    user_id: str = Depends(user_id_extractor), 
    course_service: CourseService = Depends(CourseService)
):
    await course_service.generate_course(user_id, payload)
    
@router.get("/{course_id}/exercises", dependencies=[Depends(user_id_extractor)])
async def get_exercises(
    course_id: uuid.UUID,
    course_service: CourseService = Depends(CourseService)
):
    return course_service.get_exercises(course_id)

@router.get("/trigger/{course_id}", dependencies=[Depends(user_id_extractor)])
async def trigger_course_generation(
    course_id: uuid.UUID,
    user_id: str = Depends(user_id_extractor)
):
    producer = KafkaProducer()
    producer.produce_message(
        topic=Topic.COURSE_GENERATED,
        message=CourseGeneratedTopic(user_id=uuid.UUID(user_id), course_id=course_id)
    )
    
    return {"message": "Course generation triggered"}