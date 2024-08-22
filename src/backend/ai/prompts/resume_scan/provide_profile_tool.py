from ai.common import BaseTool
from .models import ProfileScan

class ProvideProfileTool(BaseTool):
    result: ProfileScan
    
    def __init__(self):
        super().__init__("provide_profile", "Provides the user with the processed profile information")
        
        profile_schema = ProfileScan.model_json_schema()
        
        self.use_schema(profile_schema)
        
    def process(self, arguments: dict) -> str:
        self.result = arguments
        
        return "Success"