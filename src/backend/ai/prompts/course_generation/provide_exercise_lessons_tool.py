from pydantic import BaseModel
from ai.common.base_tool import BaseTool
from ai.util.pydantic_inline_refs import pydantic_inline_ref_schema

class ResponseModel(BaseModel):
    reason: str
    lesson_ids: list[str]

class ProvideExerciseLessonsTool(BaseTool):
    result: ResponseModel
    
    def __init__(self):
        super().__init__("provide_lessons", "Provides the IDs of each lesson that should be used to generate exercises")
        pydantic_schema = ResponseModel.model_json_schema()
        inline_schema = pydantic_inline_ref_schema(pydantic_schema)
        self.use_schema(inline_schema)
        
    def process(self, arguments: dict):
        self.result = arguments
        
        return "Success"