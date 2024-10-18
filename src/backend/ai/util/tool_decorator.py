import inspect
import logging
from typing import Callable, Any, get_type_hints, List, Union, get_origin, get_args, Dict, Awaitable, Optional, Literal
from enum import Enum
from pydantic import BaseModel
from ai.common import BaseTool
from .pydantic_inline_refs import pydantic_inline_ref_schema
import ai.prompts as prompts

logging.basicConfig(level=logging.INFO)

# Global registry to store all decorated tools
TOOL_REGISTRY: Dict[str, 'ToolWrapper'] = {}

def tool(description: str, is_public: bool = False, force_if: Optional[Callable[['prompts.base_prompt.BasePrompt'], bool]] = None):
    """
    A decorator to create an async tool from a class method.
    
    Args:
        description (str): The description of the tool.
        is_public (bool): Whether the tool is public.
        force_if (Optional[Callable[['BasePrompt'], bool]]): A callable that determines if the tool should be forced.
    
    Returns:
        Callable: A decorator function.
    """
    def decorator(func: Callable[..., Awaitable[Any]]) -> 'ToolWrapper':
        tool_wrapper = ToolWrapper(func, description)
        tool_wrapper.is_public = is_public
        tool_wrapper.force_if = force_if
        tool_key = f"{func.__module__}.{func.__name__}"
        TOOL_REGISTRY[tool_key] = tool_wrapper
        return tool_wrapper

    return decorator

class ToolWrapper(BaseTool):
    def __init__(self, func: Callable[..., Awaitable[Any]], description: str):
        super().__init__(func.__name__, description)
        self.func = func
        self.use_schema(self._generate_schema())
        self.is_public = False
        self.force_if: Optional[Callable[['prompts.base_prompt.BasePrompt'], bool]] = None

    async def process(self, instance: Any, arguments: dict) -> Any:
        return await self.func(instance, **arguments)

    def _generate_schema(self) -> dict:
        params = inspect.signature(self.func).parameters
        type_hints = get_type_hints(self.func)
        
        properties = {}
        required = []

        for name, param in params.items():
            # Skip the 'self' parameter
            if name == 'self':
                continue
            param_type = type_hints.get(name, Any)
            properties[name] = self._get_property_schema(param_type)
            if param.default == inspect.Parameter.empty:
                required.append(name)

        schema = {
            "type": "object",
            "properties": properties,
            "required": required
        }
        
        logging.info(f"Generated schema for {self.func.__name__}: {schema}")
        
        return schema

    def _get_property_schema(self, param_type: type) -> dict:
        logging.info(f"Getting property schema for {param_type}")
        
        # Check for basic types first
        if param_type == str:
            return {"type": "string"}
        elif param_type == int:
            return {"type": "integer"}
        elif param_type == float:
            return {"type": "number"}
        elif param_type == bool:
            return {"type": "boolean"}
        
        # Check for generic types
        origin = get_origin(param_type)
        if origin is not None:
            if origin == list or origin == List:
                item_type = get_args(param_type)[0]
                return {
                    "type": "array",
                    "items": self._get_property_schema(item_type)
                }
            elif origin == Union:
                # Handle Optional types (Union[T, None])
                types = get_args(param_type)
                if len(types) == 2 and types[1] == type(None):
                    return self._get_property_schema(types[0])
            elif origin == Literal:
                literal_values = get_args(param_type)
                return {
                    "type": "string",
                    "enum": list(literal_values)
                }
        
        # Check for more complex types
        if isinstance(param_type, type):
            if issubclass(param_type, BaseModel):
                inline_schema = param_type.model_json_schema()
                inline_schema = pydantic_inline_ref_schema(inline_schema)
                return inline_schema
            elif issubclass(param_type, Enum):
                return {
                    "type": "string",
                    "enum": [e.value for e in param_type]
                }
        
        # Default case
        logging.warning(f"Unknown type: {param_type}. Returning empty schema.")
        return {}  # Default to an empty schema for unknown types
