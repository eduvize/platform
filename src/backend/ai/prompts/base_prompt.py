import json
import logging
from typing import Dict, List, Optional, Type, TypeVar, cast, get_type_hints

from pydantic import BaseModel
from pydantic_core import ValidationError
from ai.common import BaseChatMessage, BaseTool, ChatRole, BaseToolCallWithResult

T = TypeVar('T', bound='BaseTool')

class BasePrompt:
    system_prompt: str
    messages: List[BaseChatMessage]
    tools: List[BaseTool]
    tool_types: Dict[str, Type[BaseTool]]
    tool_result_types: Dict[str, Type]
    tool_instances: Dict[str, List[BaseTool]]
    forced_tool_name: Optional[str] = None
    tool_choice_filter: Optional[list[str]] = None
     
    def __init__(self) -> None:
        self.system_prompt = None
        self.messages = []
        self.tools = []
        self.tool_types = {}
        self.tool_result_types = {}
        self.tool_instances = {}
        
        self.setup()
    
    def setup(self) -> None:
        raise NotImplementedError("Method not implemented")
    
    def set_system_prompt(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        
    def use_tool(self, tool_type: Type[BaseTool], force: Optional[bool] = False) -> None:
        inst = tool_type()
        self.tools.append(inst)
        self.tool_types[inst.name] = tool_type
        self.tool_instances[tool_type.__name__] = []
        
        # Get the Type annotation of the tool's "result" property
        result_type = get_type_hints(tool_type).get("result")

        if not result_type:
            raise ValueError(f"Tool {tool_type.__name__} does not have a 'result' property defined with a type hint")
        
        self.tool_result_types[inst.name] = result_type
        
        logging.info(f"{tool_type.__name__} has result type {result_type.__name__}")
        
        if force:
            self.force_tool(tool_type)
            
    def require_one_of_tools(self, tool_types: list[Type[BaseTool]]) -> None:
        self.forced_tool_name = None
        self.tool_choice_filter = [tool_type().name for tool_type in tool_types]
        
    def force_tool(self, tool_type: Type[BaseTool]) -> None:
        inst = tool_type()
        self.forced_tool_name = inst.name
        self.tool_choice_filter = None
        
    def process_tool(self, tool_name: str, arguments: dict):
        if tool_name not in self.tool_types:
            raise ValueError(f"Tool {tool_name} not found when processing")
        
        tool_type = self.tool_types[tool_name]
        inst = tool_type()
        tool_response = inst.process(arguments)
        
        try:
            pydantic_cast = cast(BaseModel, self.tool_result_types[tool_name])
            
            validated_data = pydantic_cast.model_validate(inst.result)
            
            inst.result = validated_data
            
            self.tool_instances[tool_type.__name__].append(inst)
            
            return tool_response
        except ValidationError as validation_error:
            logging.info(f"Validation error: {validation_error}")
            logging.info(inst.result)
            
            errors = []
            
            for error in validation_error.errors():
                # Join the full location path for clarity
                error_loc = " -> ".join(map(str, error['loc']))
                error_str = f"{error_loc}: {error['msg']}"
                
                if error_str not in errors:
                    errors.append(error_str)
                
            raise ValueError(f"Tool {tool_name} result validation failed: {', '.join(errors)}")
    
    def is_tool_public(self, tool_name: str) -> bool:
        if tool_name not in self.tool_types:
            return False
        
        return hasattr(self.tool_types[tool_name], "IS_PUBLIC")
    
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
