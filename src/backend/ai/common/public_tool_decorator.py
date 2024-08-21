from typing import Callable, Type
from ai.common.base_tool import BaseTool

def public_tool() -> Callable:
    """
    A decorator that labels a tool as public by adding an 'IS_PUBLIC' attribute to the class.

    Returns:
        Callable: The decorated class with the 'IS_PUBLIC' attribute set to True
    """
    
    def decorator(tool: Type[BaseTool]) -> Type[BaseTool]:
        tool.IS_PUBLIC = True
        
        return tool
    
    return decorator
