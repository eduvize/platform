import logging
from ai.common.base_tool import BaseTool
from .models import CourseOutline

class ProvideCourseOutlineTool(BaseTool):
    result: CourseOutline
    
    def __init__(self):
        super().__init__("provide_course_outline", "Provides the outline to the course")
        self.use_schema(CourseOutline.model_json_schema())
        logging.info(CourseOutline.model_json_schema())
        
    def process(self, arguments: dict):
        self.result = arguments
        
        return "Course outline successfully saved"