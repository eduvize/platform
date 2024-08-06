import json
import base64
from typing import Generator, List, Literal, Tuple, cast
from openai import OpenAI, Stream
from openai.types.chat.chat_completion_assistant_message_param import FunctionCall
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionAssistantMessageParam, 
    ChatCompletionUserMessageParam, 
    ChatCompletionToolMessageParam, 
    ChatCompletionToolParam, 
    ChatCompletionContentPartTextParam,
    ChatCompletionContentPartImageParam,
    ChatCompletionMessageToolCall, 
    ChatCompletionChunk
)
from openai.types.chat.chat_completion_content_part_image_param import ImageURL
from openai.types.shared import FunctionDefinition
from config import get_openai_key
from . import BaseModel
from app.ai.prompts import BasePrompt
from app.common import BaseChatMessage, BaseChatResponse, BaseTool, ChatRole

class ToolCallRecord:
    index: int
    id: str
    name: str
    arguments: dict
    result: str
    
    def __init__(self, index: int, id: str, name: str, arguments: dict) -> None:
        self.index = index
        self.id = id
        self.name = name
        self.arguments = arguments
        self.result = "Success"

class BaseGPT(BaseModel):
    client: OpenAI
    model_name: str
    
    def __init__(self, model_name: str) -> None:
        api_key = get_openai_key()
        
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name 
    
    def get_streaming_response(self, prompt: BasePrompt) -> Generator[Tuple[str, str], None, List[BaseChatResponse]]:
        responses: List[BaseChatResponse] = []
        
        # Create an initial message list based on the prompt, this may be added to later
        messages = [self.get_message(message) for message in prompt.messages]
        
        if prompt.system_prompt:
            messages.insert(0, ChatCompletionSystemMessageParam(role="system", content=prompt.system_prompt))
        
        # Map tool instances to their names and create tool calls
        tool_instances = {tool.name: tool for tool in prompt.tools}
        tool_calls = [self.get_tool(tool) for tool in prompt.tools]
        
        # Loops until there are no more tool calls to process
        while True:
            response = cast(Stream[ChatCompletionChunk], self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tool_calls,
                stream=True
            ))
            
            response_content: str = ""
            tool_call_dict: List[ToolCallRecord] = []
            finish_reason: Literal['stop', 'length', 'tool_calls', 'content_filter', 'function_call']
            
            # Iterate through the completion stream
            # Yield text content as it is received
            # Collect tool calls as they populate
            for chunk in response:
                tool_calls = chunk.choices[0].delta.tool_calls
                content = chunk.choices[0].delta.content
                
                if content:
                    yield chunk.id, content
                    
                if tool_calls:
                    for tool_call in tool_calls:
                        existing_record = next((record for record in tool_call_dict if record.index == tool_call.index), None)
                        
                        if existing_record is None:
                            if tool_call.function:
                                t_arguments = tool_call.function.arguments
                            else:
                                t_arguments = ""
                            
                            tool_call_dict.append(ToolCallRecord(
                                index=tool_call.index,
                                id=tool_call.id,
                                name=tool_call.function.name,
                                arguments=t_arguments
                            ))
                        else:
                            existing_record.arguments += tool_call.function.arguments
                            
                if chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason
                    break
            
            # Execute any tools that were called
            if len(tool_call_dict) > 0:
                for record in tool_call_dict:
                    # Try to load the JSON - if it fails, return an error to the model for correction
                    try:
                        json_dict = json.loads(record.arguments)
                        record.result = prompt.process_tool(tool_name=record.name, arguments=json_dict)
                    except json.JSONDecodeError:
                        record.result = "Invalid json arguments"
                
            # Build the response message
            response_message = ChatCompletionAssistantMessageParam(
                role="assistant",
                content=response_content,
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id=record.id,
                        type="function",
                        function=FunctionCall(
                            name=record.name,
                            arguments=record.arguments
                        )
                    ) for record in tool_call_dict
                ]
            )
            
            responses.append(
                BaseChatResponse(
                    response_content, 
                    [
                        ChatCompletionToolMessageParam(
                            tool_call_id=record.id, 
                            content=record.result
                        ) for record in tool_call_dict
                    ]
                )
            )
            
            # If the finish reason is tool calls, added to the chat context and repeat the loop
            if finish_reason == "tool_calls":
                messages.append(response_message)
                
                for record in tool_call_dict:
                    messages.append(ChatCompletionToolMessageParam(role="tool", tool_call_id=record.id, content=record.result))
                
                continue
            else:
                break
            
        return responses
        
    def get_message(self, message: BaseChatMessage) -> dict:
        if message.role == ChatRole.USER:
            # If images are included, write content out as an array of parts
            if message.png_images:
                base64_images = [
                    f"data:image/png;base64,{base64_str}" 
                    for base64_str in [
                        base64.b64encode(image).decode("ascii") 
                        for image in message.png_images
                    ]
                ]
                
                return ChatCompletionUserMessageParam(
                    role="user",
                    content=[
                        ChatCompletionContentPartTextParam(
                            type="text",
                            text=message.message
                        ),
                        *[
                            ChatCompletionContentPartImageParam(
                                type="image_url",
                                image_url=ImageURL(url=image)
                            ) for image in base64_images
                        ]
                    ]
                )
                
            return ChatCompletionUserMessageParam(role="user", content=message.message)
        elif message.role == ChatRole.AGENT:
            return ChatCompletionAssistantMessageParam(role="assistant", content=message.message)
        elif message.role == ChatRole.TOOL:
            return ChatCompletionToolMessageParam(role="tool", content=message.message)
        
    def get_tool(self, tool: BaseTool) -> dict:
        return ChatCompletionToolParam(
            type="function",
            function=FunctionDefinition(
                name=tool.name,
                description=tool.description,
                parameters=tool.schema
            )
        )