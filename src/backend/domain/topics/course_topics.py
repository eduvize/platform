import uuid
from pydantic import BaseModel
from ai.prompts.course_generation.models import CourseOutline

class CourseGenerationTopic(BaseModel):
    user_id: uuid.UUID
    course_id: uuid.UUID
    course_outline: CourseOutline
    
class CourseGeneratedTopic(BaseModel):
    user_id: uuid.UUID
    course_id: uuid.UUID