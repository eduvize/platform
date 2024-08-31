from typing import List

from pydantic import BaseModel
from ai.common import BaseTool

class ResultObject(BaseModel):
    options: List[str]

class ProvideOptionsTool(BaseTool):
    result: ResultObject
    
    def __init__(self):
        super().__init__("provide_options", "Returns a list of options to choose from")
        self.use_schema(ResultObject.model_json_schema())
        
    def process(self, arguments: dict) -> str:
        self.result = arguments
        
        return "Success"