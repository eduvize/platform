import pytest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel
from ai.prompts.base_prompt import BasePrompt, BaseTool, BaseChatMessage, ChatRole

class TestPrompt(BasePrompt):
    def setup(self) -> None:
        pass
    
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


@patch("ai.prompts.base_prompt.get_type_hints", return_value={"result": str})
def test_use_tool_adds_tool(mock_get_type_hints, base_prompt):
    """
    Test the `use_tool` method.
    
    - Assert that a tool is added to `tools` after calling `use_tool`.
    - Assert that the tool's type is stored in `tool_types`.
    - Assert that the tool's result type is stored in `tool_result_types`.
    """
    base_prompt.use_tool(MockTool)
    
    assert len(base_prompt.tools) == 1
    assert isinstance(base_prompt.tools[0], MockTool)
    assert base_prompt.tool_types["mock_tool"] == MockTool
    assert base_prompt.tool_result_types["mock_tool"] == str

@patch("ai.prompts.base_prompt.get_type_hints")
def test_use_tool_raises_value_error_on_missing_result_type(mock_get_type_hints, base_prompt):
    """
    Test the `use_tool` method raises a ValueError when a tool does not have a `result` type annotation.
    
    - Assert that ValueError is raised when the tool has no result type hint.
    """
    mock_get_type_hints.return_value = MagicMock(get=MagicMock(return_value=None))
    
    with pytest.raises(ValueError):
        base_prompt.use_tool(MockToolWithoutResult)


def test_force_tool(base_prompt):
    """
    Test the `force_tool` method.
    
    - Assert that the forced tool's name is set correctly.
    - Assert that `tool_choice_filter` is reset to None.
    """
    base_prompt.force_tool(MockTool)
    
    assert base_prompt.forced_tool_name == "mock_tool"
    assert base_prompt.tool_choice_filter is None


def test_process_tool_raises_on_missing_tool(base_prompt):
    """
    Test the `process_tool` method raises a ValueError if the tool is not found.
    
    - Assert that a ValueError is raised when the tool does not exist.
    """
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


def test_require_one_of_tools(base_prompt):
    """
    Test the `require_one_of_tools` method.
    
    - Assert that the forced tool name is set to None.
    - Assert that the tool choice filter is set with the names of the provided tools.
    """
    base_prompt.require_one_of_tools([MockTool])
    
    assert base_prompt.forced_tool_name is None
    assert base_prompt.tool_choice_filter == ["mock_tool"]
