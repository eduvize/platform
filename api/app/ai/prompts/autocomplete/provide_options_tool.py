from typing import List
from ...common import BaseTool

class ProvideOptionsTool(BaseTool):
    def __init__(self):
        super().__init__("provide_options", "Returns a list of options to choose from")
        self.use_schema({
            "type": "object",
            "properties": {
                "options": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": ["options"]
        })
        
    def process(self, arguments: dict) -> str:
        if arguments["options"]:
            self.result = arguments["options"]
        else:
            self.result = []
        
        return "Success"