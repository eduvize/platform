import json
import logging
from ai.common import BaseTool
from domain.dto.courses import CourseDto
from ai.common import public_tool

@public_tool()
class ProvideCourseOutlineTool(BaseTool):
    def __init__(self):
        super().__init__("provide_course_outline", "Displays the course outline for the user to view on the UI")
        self.use_schema(CourseDto.model_json_schema())
        
    def process(self, arguments: dict) -> str:
        self.result = arguments
        
        logging.info(json.dumps(CourseDto.model_json_schema(), indent=4))
        
        logging.info(json.dumps(arguments, indent=4))
                
        return "Success"