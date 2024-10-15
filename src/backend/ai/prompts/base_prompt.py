import json
import logging
from typing import Dict, List, Optional, Type, TypeVar, cast, get_type_hints, Any

from pydantic import BaseModel
from pydantic_core import ValidationError
from ai.common import BaseChatMessage, BaseTool, ChatRole, BaseToolCallWithResult
from ai.util.tool_decorator import TOOL_REGISTRY

T = TypeVar('T', bound='BaseTool')

class BasePrompt:
    system_prompt: str
    messages: List[BaseChatMessage]
    tools: List[str]  # Now we store tool names instead of BaseTool instances
    tool_types: Dict[str, Type[BaseTool]]
    tool_result_types: Dict[str, Type]
    tool_instances: Dict[str, List[BaseTool]]
    forced_tool_name: Optional[str] = None
    tool_choice_filter: Optional[list[str]] = None
    forced_tools: List[str] = []
     
    def __init__(self, system_prompt: Optional[str] = None, tools: List[str] = None) -> None:
        self.messages = []
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.tool_types = {}
        self.tool_result_types = {}
        self.tool_instances = {}
        self.forced_tools = []
        
        self.setup()
    
    def setup(self) -> None:
        pass
    
    def set_system_prompt(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        
    def use_tool(self, tool_type: Type[BaseTool], force: Optional[bool] = False) -> None:
        pass
            
    def require_one_of_tools(self, tool_types: list[Type[BaseTool]]) -> None:
        pass
        
    def force_tool(self, tool_type: Type[BaseTool]) -> None:
        tool_name = tool_type.__name__
        if tool_name not in self.tools:
            self.tools.append(tool_name)
        if tool_name not in self.forced_tools:
            self.forced_tools.append(tool_name)

    def unforce_tool(self, tool_type: Type[BaseTool]) -> None:
        tool_name = tool_type.__name__
        if tool_name in self.forced_tools:
            self.forced_tools.remove(tool_name)

    def is_tool_public(self, tool_name: str) -> bool:
        return tool_name in self.tools
    
    def get_tool_call(self, tool_type: Type[T]) -> Optional[T]:
        if tool_type.__name__ not in self.tool_instances:
            return None
        
        calls = self.tool_instances[tool_type.__name__]
        
        if len(calls) == 0:
            return None
        
        return calls[-1]
        
    def add_user_message(self, message: str, png_images: List[bytes] = []) -> None:
        self.messages.append(BaseChatMessage(role=ChatRole.USER, message=message, png_images=png_images))
        
    def add_agent_message(self, message: str, tool_calls: Optional[List[BaseToolCallWithResult]] = None) -> None:
        self.messages.append(BaseChatMessage(role=ChatRole.AGENT, message=message, tool_calls=tool_calls or []))
