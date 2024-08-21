from typing import List
from .base_message import BaseChatMessage, ChatRole
from .base_tool import BaseToolCallWithResult

class BaseChatResponse(BaseChatMessage):
    tool_calls: List[BaseToolCallWithResult]
    
    def __init__(self, message: str, tool_calls: List[BaseToolCallWithResult]):
        super().__init__(ChatRole.AGENT, message)
        self.tool_calls = tool_calls