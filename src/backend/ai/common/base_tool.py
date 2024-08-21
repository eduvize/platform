from typing import Optional

class BaseTool:
    name: str
    description: str
    schema: dict
    result: Optional[dict]
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
    def use_schema(self, schema: dict) -> None:
        self.schema = schema
        
    def process(arguments: dict):
        raise NotImplementedError("Method not implemented")
        
class BaseToolCall:
    id: str
    name: str
    arguments: str
    
    def __init__(self, id: str, name: str, arguments: str):
        self.id = id
        self.name = name
        self.arguments = arguments
        
class BaseToolCallWithResult(BaseToolCall):
    result: str
    
    def __init__(
        self, 
        id: str, 
        name: str, 
        arguments: str, 
        result: str
    ):
        super().__init__(
            id, 
            name, 
            arguments
        )
        
        self.result = result