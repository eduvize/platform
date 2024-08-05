from typing import Dict, List, Type, TypeVar
from ..common import BaseChatMessage, BaseTool, ChatRole

T = TypeVar('T', bound='BaseTool')

class BasePrompt:
    system_prompt: str
    messages: List[BaseChatMessage]
    tools: List[BaseTool]
    tool_types: Dict[str, Type[BaseTool]]
    tool_instances: Dict[str, List[BaseTool]]
     
    def __init__(self) -> None:
        self.system_prompt = None
        self.messages = []
        self.tools = []
        self.tool_types = {}
        self.tool_instances = {}
        
        self.setup()
    
    def setup(self) -> None:
        raise NotImplementedError("Method not implemented")
    
    def set_system_prompt(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        
    def use_tool(self, tool_type: Type[BaseTool]) -> None:
        inst = tool_type()
        self.tools.append(inst)
        self.tool_types[inst.name] = tool_type
        self.tool_instances[tool_type.__name__] = []
        
    def process_tool(self, tool_name: str, arguments: dict):
        if tool_name not in self.tool_types:
            raise ValueError(f"Tool {tool_name} not found when processing")
        
        tool_type = self.tool_types[tool_name]
        inst = tool_type()
        result = inst.process(arguments)
        
        self.tool_instances[tool_type.__name__].append(inst)
        
        return result
    
    def get_tool_calls(self, tool_type: Type[T]) -> List[T]:
        if tool_type.__name__ not in self.tool_instances:
            return []
        
        return self.tool_instances[tool_type.__name__]
        
    def add_user_message(self, message: str, png_images: List[bytes] = []) -> None:
        self.messages.append(BaseChatMessage(role=ChatRole.USER, message=message, png_images=png_images))
        
    def add_agent_message(self, message: str) -> None:
        self.messages.append(BaseChatMessage(role=ChatRole.AGENT, message=message))
        
    def with_input(self, message: str) -> "BasePrompt":
        self.add_user_message(message)
        
        return self