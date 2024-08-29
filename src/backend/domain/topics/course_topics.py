import uuid
from pydantic import BaseModel
from ai.prompts.course_generation.models import CourseOutline

class CourseGenerationTopic(BaseModel):
    course_id: uuid.UUID
    course_outline: CourseOutline