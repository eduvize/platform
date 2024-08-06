from app.ai.common import BaseTool
from domain.dto.user import UserProfileDto

class ProvideProfileTool(BaseTool):
    def __init__(self):
        super().__init__("provide_profile", "Provides the user with the processed profile information")
        
        profile_schema = UserProfileDto.model_json_schema()
        
        self.use_schema(profile_schema)
        
    def process(self, arguments: dict) -> str:
        self.result = arguments
        
        return "Success"