from typing import Optional
from pydantic import BaseModel
from domain.enums.course_enums import CourseMotivation, CurrentSubjectExperience, CourseMaterial

from enum import Enum
from typing import Optional
from pydantic import BaseModel

class InputType(Enum):
    TEXT = "text"
    SELECT = "select"
    MULTISELECT = "multiselect"

class InputField(BaseModel):
    required: bool
    name: str
    short_label: str
    description: Optional[str] = None
    input_type: InputType
    options: Optional[list[str]] = None
    depends_on_input_name: Optional[str] = None
    depends_on_input_value: Optional[str] = None

class AdditionalInputs(BaseModel):
    inputs: list[InputField]

class CoursePlanDto(BaseModel):
    subject: str
    motivations: list[CourseMotivation]
    other_motivation_details: Optional[str] = None
    experience: CurrentSubjectExperience
    experience_details: Optional[str] = None
    materials: list[CourseMaterial]
    challanges: Optional[str] = None
    desired_outcome: str
    followup_answers: Optional[dict] = None
