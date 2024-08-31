from ai.common.base_tool import BaseTool
from domain.dto.courses import AdditionalInputs
from ai.util import pydantic_inline_ref_schema

class ProvideAdditionalInputsTool(BaseTool):
    result: AdditionalInputs
    
    def __init__(self):
        super().__init__("provide_additional_inputs", "Provides additional inputs for the user to complete the course planning process")
        json_schema = AdditionalInputs.model_json_schema()
        inline_schema = pydantic_inline_ref_schema(json_schema)
        self.use_schema(inline_schema)
        
    def process(self, arguments: dict) -> str:
        self.result = arguments
        
        return "Success"