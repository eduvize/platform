from ai.common.base_tool import BaseTool
from ai.util.pydantic_inline_refs import pydantic_inline_ref_schema
from domain.dto.playground.environment_setup_instructions import EnvironmentSetupInstructions

class ProvideInstructionsTool(BaseTool):
    result: EnvironmentSetupInstructions
    
    def __init__(self):
        super().__init__("provide_instructions", "Provides the final set of environment setup instructions.")
        json_schema = EnvironmentSetupInstructions.model_json_schema()
        inline_schema = pydantic_inline_ref_schema(json_schema)
        self.use_schema(inline_schema)
        
    def process(self, arguments: dict) -> str:
        self.result = arguments
        
        return "Success"