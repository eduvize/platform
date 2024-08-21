import uuid
from domain.schema.courses.course import Course

class CourseRepository:
    def create_course(
        self,
        user_id: uuid.UUID,
        course: Course
    ):
        pass