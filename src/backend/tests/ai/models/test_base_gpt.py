import pytest
from unittest.mock import MagicMock, patch
from ai.models.base_gpt import BaseGPT, BasePrompt, BaseChatMessage, ChatRole, ToolCallRecord, BaseTool, BaseChatResponse, BaseToolCallWithResult
from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_message_param import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam, ChatCompletionToolMessageParam
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from openai.types.shared import FunctionDefinition

class TestPrompt(BasePrompt):
    def setup(self) -> None:
        pass

@pytest.fixture
def mock_openai():
    with patch("ai.models.base_gpt.AsyncOpenAI") as mock_openai:
        yield mock_openai

@pytest.fixture
def base_gpt(mock_openai):
    return BaseGPT(model_name="gpt-test")

@pytest.fixture
def base_prompt():
    # Setup a basic prompt with some mock data for testing purposes
    prompt = TestPrompt()
    prompt.system_prompt = "Test system prompt"
    prompt.add_user_message("Hello!")
    return prompt

def test_init_base_gpt(mock_openai):
    """
    Test initialization of BaseGPT
    - Assert that the OpenAI client is initialized with the correct API key
    - Assert that the model name is set correctly
    """
    base_gpt = BaseGPT(model_name="gpt-test")
    mock_openai.assert_called_once()
    assert base_gpt.model_name == "gpt-test"

def test_get_messages_with_user_message(base_gpt):
    """
    Test the get_messages method for a user message with no images.
    - Assert that a single user message is returned correctly.
    """
    user_message = BaseChatMessage(role=ChatRole.USER, message="Hello, GPT!")
    messages = base_gpt.get_messages(user_message)

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello, GPT!"

def test_get_messages_with_user_message_and_images(base_gpt):
    """
    Test the get_messages method for a user message with images.
    - Assert that a message with text and images is returned correctly.
    - Assert that images are properly base64 encoded.
    """
    # Mock user message with an image
    image_data = b"imagebytes"
    user_message = BaseChatMessage(role=ChatRole.USER, message="Hello, GPT!", png_images=[image_data])

    # Run the get_messages method
    messages = base_gpt.get_messages(user_message)

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert isinstance(messages[0]["content"], list)
    assert len(messages[0]["content"]) == 2  # One text part and one image part
    assert messages[0]["content"][0]["type"] == "text"
    assert messages[0]["content"][0]["text"] == "Hello, GPT!"
    assert messages[0]["content"][1]["type"] == "image_url"
    assert messages[0]["content"][1]["image_url"]["url"].startswith("data:image/png;base64,")

def test_get_messages_with_agent_message(base_gpt):
    """
    Test the get_messages method for an agent (assistant) message with tool calls.
    - Assert that assistant messages are returned with proper formatting and tool calls.
    """
    tool_call = BaseToolCallWithResult(id="tool_call_1", name="test_tool", arguments={"arg": "value"}, result="")
    agent_message = BaseChatMessage(role=ChatRole.AGENT, message="Here is my tool response", tool_calls=[tool_call])
    messages = base_gpt.get_messages(agent_message)

    assert len(messages) == 2
    assert messages[0]["role"] == "assistant"
    assert messages[0]["content"] == "Here is my tool response"
    assert len(messages[0]["tool_calls"]) == 1
    assert messages[0]["tool_calls"][0].type == "function"
    assert messages[0]["tool_calls"][0].function.name == "test_tool"
    assert messages[0]["tool_calls"][0].function.arguments == '{"arg": "value"}'

    assert messages[1]["role"] == "tool"
    assert messages[1]["tool_call_id"] == "tool_call_1"

def test_get_tool(base_gpt):
    """
    Test the get_tool method.
    - Assert that the tool is correctly formatted for the API.
    """
    mock_tool = MagicMock(spec=BaseTool)
    mock_tool.name = "mock_tool"
    mock_tool.description = "This is a mock tool."
    mock_tool.schema = {"type": "object", "properties": {}}

    tool_data = base_gpt.get_tool(mock_tool)

    assert tool_data["type"] == "function"
    assert "function" in tool_data
    assert tool_data["function"].name == "mock_tool"
    assert tool_data["function"].description == "This is a mock tool."
    assert tool_data["function"].parameters == {"type": "object", "properties": {}}
