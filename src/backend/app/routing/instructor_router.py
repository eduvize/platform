from fastapi import APIRouter, Depends, Response
from app.services.instructor_service import InstructorService
from domain.dto.instructors import InstructorDto

router = APIRouter(
    prefix="/instructors",
)

@router.get("/{instructor_id}/profile-photo", response_class=Response)
async def get_instructor_profile_photo(
    instructor_id: str,
    instructor_service: InstructorService = Depends(InstructorService)
):
    """
    Retrieve the profile photo of an instructor.

    Args:
        instructor_id (str): The ID of the instructor.
        instructor_service (InstructorService): The service to handle instructor-related operations.

    Returns:
        Response: The profile photo as a PNG image.
    """
    photo_bytes = await instructor_service.get_instructor_profile_photo(instructor_id)
    return Response(content=photo_bytes, media_type="image/png")

@router.get("/", response_model=list[InstructorDto])
async def get_instructors(
    instructor_service: InstructorService = Depends(InstructorService)
):
    return await instructor_service.get_all_instructors()
