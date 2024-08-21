import uuid
from sqlmodel import Session
from domain.dto.courses.course import CourseDto

def map_course_data(
    session: Session, 
    user_id: uuid.UUID, 
    course_dto: CourseDto
):
    pass