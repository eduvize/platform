import logging
from pydantic import BaseModel
from ai.common.base_tool import BaseTool
from domain.dto.courses import ExercisePlan
from ai.util.pydantic_inline_refs import pydantic_inline_ref_schema

class ProvideExerciseTool(BaseTool):
    result: ExercisePlan
    
    def __init__(self):
        super().__init__("add_exercise", "Adds an exercise to the course")
        pydantic_schema = ExercisePlan.model_json_schema()
        inline_schema = pydantic_inline_ref_schema(pydantic_schema)
        self.use_schema(inline_schema)
        
    def process(self, arguments: dict):
        self.result = arguments
        
        return "Success"