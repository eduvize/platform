from enum import Enum
from typing import List, Optional

class ChatRole(Enum):
    USER = 1
    AGENT = 2
    TOOL = 3

class BaseChatMessage:
    role: ChatRole
    message: str
    
    def __init__(self, role: ChatRole, message: str):
        self.role = role
        self.message = message

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
    arguments: dict
    
    def __init__(self, id: str, name: str, arguments: dict):
        self.id = id
        self.name = name
        self.arguments = arguments
        
class BaseChatResponse(BaseChatMessage):
    tool_calls: List[BaseToolCall]
    
    def __init__(self, message: str, tool_calls: List[BaseToolCall]):
        super().__init__(ChatRole.AGENT, message)
        self.tool_calls = tool_calls