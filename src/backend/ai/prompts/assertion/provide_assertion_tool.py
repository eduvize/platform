from ai.common import BaseTool
from .models import AssertionResult

class ProvideAssertionTool(BaseTool):
    def __init__(self):
        super().__init__("provide_assertion", "Provides the user with the processed assertion information")
        
        self.use_schema(AssertionResult.model_json_schema())
        
    def process(self, arguments: dict) -> str:
        self.result = AssertionResult(**arguments)
        
        return "Success"