from typing import Literal, Optional, List
from pydantic import BaseModel

class SetupStep(BaseModel):
    step_type: Literal["shell_command", "write_file"]
    summary_text: str
    command_str: Optional[str] = None
    file_path: Optional[str] = None
    file_contents: Optional[str] = None

class EnvironmentSetupInstructions(BaseModel):
    steps: List[SetupStep] = []
    