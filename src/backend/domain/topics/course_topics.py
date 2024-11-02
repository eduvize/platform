import uuid
from pydantic import BaseModel
from ai.prompts.generate_course_outline_prompt import CourseOutline

class CourseCreatedTopic(BaseModel):
    user_id: uuid.UUID
    course_id: uuid.UUID
    course_title: str
    course_description: str
    key_outcomes: list[str]
    topics: list[str]

class CourseGenerationTopic(BaseModel):
    user_id: uuid.UUID
    course_id: uuid.UUID
    course_outline: CourseOutline
    
class CourseGeneratedTopic(BaseModel):
    user_id: uuid.UUID
    course_id: uuid.UUID