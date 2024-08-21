from ai.common.base_tool import BaseTool
from domain.dto.courses import AdditionalInputs

class ProvideAdditionalInputsTool(BaseTool):
    def __init__(self):
        super().__init__("provide_additional_inputs", "Provides additional inputs for the user to complete the course planning process")
        self.use_schema(AdditionalInputs.model_json_schema())
        
    def process(self, arguments: dict) -> str:
        self.result = arguments
        
        return "Success"