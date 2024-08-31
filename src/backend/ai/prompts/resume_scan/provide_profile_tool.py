from ai.common import BaseTool
from .models import ProfileScan
from ai.util import pydantic_inline_ref_schema

class ProvideProfileTool(BaseTool):
    result: ProfileScan
    
    def __init__(self):
        super().__init__("provide_profile", "Provides the user with the processed profile information")
        
        json_schema = ProfileScan.model_json_schema()
        inline_schema = pydantic_inline_ref_schema(json_schema)
        
        self.use_schema(inline_schema)
        
    def process(self, arguments: dict) -> str:
        self.result = arguments
        
        return "Success"