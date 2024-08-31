import logging
from ai.common.base_tool import BaseTool
from .models import CourseOutline
from ai.util import pydantic_inline_ref_schema

class ProvideCourseOutlineTool(BaseTool):
    result: CourseOutline
    
    def __init__(self):
        super().__init__("provide_course_outline", "Provides the outline to the course")
        json_schema = CourseOutline.model_json_schema()
        inline_schema = pydantic_inline_ref_schema(json_schema)
        self.use_schema(inline_schema)
        logging.info(inline_schema)
        
    def process(self, arguments: dict):
        self.result = arguments
        
        return "Course outline successfully saved"