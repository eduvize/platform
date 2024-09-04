from enum import Enum
from typing import List, Optional
from .base_tool import BaseToolCallWithResult

class ChatRole(Enum):
    USER = 1
    AGENT = 2
    TOOL = 3

class BaseChatMessage:
    role: ChatRole
    png_images: List[bytes]
    message: Optional[str]
    tool_calls: List[BaseToolCallWithResult] = []
    
    def __init__(
        self, 
        role: ChatRole, 
        message: Optional[str], 
        png_images: List[bytes] = [],
        tool_calls: List[BaseToolCallWithResult] = []
    ):
        self.role = role
        self.message = message
        self.png_images = png_images
        self.tool_calls = tool_calls