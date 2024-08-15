from .models import InstructorProfile
from ai.common import BaseTool

class ProvideInstructorProfileTool(BaseTool):
    def __init__(self):
        super().__init__("provide_instructor", "Returns the completed instructor profile")
        self.use_schema(InstructorProfile.model_json_schema())
        
    def process(self, arguments: dict) -> str:
        if arguments["name"]:
            self.result = arguments
        else:
            return "Failure: No name provided"
        
        return "Success"