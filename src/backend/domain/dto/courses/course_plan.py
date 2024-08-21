from typing import Optional
from pydantic import BaseModel
from domain.enums.course_enums import CourseMotivation, CurrentSubjectExperience, CourseMaterial

class CoursePlanDto(BaseModel):
    subject: str
    motivations: list[CourseMotivation]
    other_motivation_details: Optional[str] = None
    experience: CurrentSubjectExperience
    experience_details: Optional[str] = None
    materials: list[CourseMaterial]
