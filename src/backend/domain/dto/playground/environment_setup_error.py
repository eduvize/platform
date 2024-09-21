from pydantic import BaseModel
from .environment_setup_instructions import EnvironmentSetupInstructions

class EnvironmentSetupErrorDto(BaseModel):
    output: str
    instructions: EnvironmentSetupInstructions