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