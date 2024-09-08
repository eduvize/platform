from ai.common import BaseTool
from domain.dto.ai.assertion_result import AssertionResultDto

class ProvideAssertionTool(BaseTool):
    result: AssertionResultDto
    
    def __init__(self):
        super().__init__("provide_assertion", "Provides the user with the processed assertion information")
        
        self.use_schema(AssertionResultDto.model_json_schema())
        
    def process(self, arguments: dict) -> str:
        self.result = arguments
        
        return "Success"