from pydantic import BaseModel
from ai.common.base_tool import BaseTool
from ai.common.public_tool_decorator import public_tool
from ai.util import pydantic_inline_ref_schema

class Result(BaseModel):
    languages: list[str]

@public_tool()
class AddProgrammingLanguagesTool(BaseTool):
    result: Result
    
    def __init__(self):
        super().__init__("add_programming_languages", "Add one or more programming languages to the user's profile")
        json_schema = Result.model_json_schema()
        inline_schema = pydantic_inline_ref_schema(json_schema)
        self.use_schema(inline_schema)

    def process(self, arguments: dict) -> str:
        self.result = arguments
        return "Programming languages added"
