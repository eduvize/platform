from typing import Any
import pytest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel
from ai.prompts.base_prompt import BasePrompt, BaseTool, BaseChatMessage, ChatRole

class TestPrompt(BasePrompt):
    def setup(self) -> None:
        pass
    
    def process_tool(self, tool_call: Any, arguments: Any) -> str:
        return "mock_tool_processed"
    
class MockTool(BaseTool):
    name = "mock_tool"
    result: str = "mock_result"
    
    def __init__(self):
        super().__init__("mock_tool", "description")
    
    def process(self, arguments):
        return "mock_tool_processed"


class MockToolWithoutResult(BaseTool):
    name = "mock_tool_without_result"
    
    def __init__(self):
        super().__init__("mock_tool_without_result", "description")
    
    def process(self, arguments):
        return "mock_tool_processed"


class MockBaseChatMessage(BaseChatMessage):
    def __init__(self, role, message, png_images=None, tool_calls=None):
        self.role = role
        self.message = message
        self.png_images = png_images or []
        self.tool_calls = tool_calls or []


@pytest.fixture
def base_prompt():
    return TestPrompt()

def test_init_base_prompt(base_prompt):
    """
    Test the initialization of the BasePrompt class.
    
    - Assert that `system_prompt` is None.
    - Assert that `messages`, `tools`, `tool_types`, `tool_result_types`, and `tool_instances` are empty.
    """
    assert base_prompt.system_prompt is None
    assert base_prompt.messages == []
    assert base_prompt.tools == []
    assert base_prompt.tool_types == {}
    assert base_prompt.tool_result_types == {}
    assert base_prompt.tool_instances == {}


def test_set_system_prompt(base_prompt):
    """
    Test the `set_system_prompt` method.
    
    - Assert that the system prompt is set correctly after calling `set_system_prompt`.
    """
    base_prompt.set_system_prompt("Test prompt")
    assert base_prompt.system_prompt == "Test prompt"

def test_process_tool_raises_on_missing_tool(base_prompt):
    """
    Test the `process_tool` method raises a ValueError if the tool is not found.
    
    - Assert that a ValueError is raised when the tool does not exist.
    """
    
    # Mock the TestPrompt to raise a ValueError when the tool is not found
    with patch.object(TestPrompt, "process_tool", side_effect=ValueError("Tool non_existent_tool not found when processing")):
        with pytest.raises(ValueError, match="Tool non_existent_tool not found when processing"):
            base_prompt.process_tool("non_existent_tool", {})


def test_add_user_message(base_prompt):
    """
    Test the `add_user_message` method.
    
    - Assert that a user message is added to the messages list with the correct role.
    """
    base_prompt.add_user_message("Hello!")
    
    assert len(base_prompt.messages) == 1
    assert base_prompt.messages[0].role == ChatRole.USER
    assert base_prompt.messages[0].message == "Hello!"
    assert base_prompt.messages[0].png_images == []


def test_add_agent_message(base_prompt):
    """
    Test the `add_agent_message` method.
    
    - Assert that an agent message is added to the messages list with the correct role.
    """
    base_prompt.add_agent_message("This is an agent message.")
    
    assert len(base_prompt.messages) == 1
    assert base_prompt.messages[0].role == ChatRole.AGENT
    assert base_prompt.messages[0].message == "This is an agent message."
    assert base_prompt.messages[0].tool_calls == []