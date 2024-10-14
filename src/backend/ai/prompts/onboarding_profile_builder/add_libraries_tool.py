from pydantic import BaseModel
from ai.common.base_tool import BaseTool
from ai.common.public_tool_decorator import public_tool
from ai.util import pydantic_inline_ref_schema

class Result(BaseModel):
    libraries: list[str]

@public_tool()
class AddLibrariesTool(BaseTool):
    result: Result
    
    def __init__(self):
        super().__init__("add_libraries", "Add one or more libraries or frameworks to the user's profile")
        json_schema = Result.model_json_schema()
        inline_schema = pydantic_inline_ref_schema(json_schema)
        self.use_schema(inline_schema)

    def process(self, arguments: dict) -> str:
        self.result = arguments
        return "Libraries added"
