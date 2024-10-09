import logging
import json
import base64

from . import BaseModel
from domain.dto.ai.completion_chunk import CompletionChunk, Tool
from typing import AsyncGenerator, List, Literal, Tuple
from openai import AsyncOpenAI
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
    ChatCompletionMessageParam
)
from openai.types.chat.chat_completion_named_tool_choice_param import Function as NamedToolFunction, ChatCompletionNamedToolChoiceParam
from openai.types.chat.chat_completion_content_part_image_param import ImageURL
from openai.types.shared import FunctionDefinition
from config import get_openai_key
from ai.prompts import BasePrompt
from ai.common import BaseChatMessage, BaseChatResponse, BaseTool, BaseToolCallWithResult, ChatRole

logger = logging.getLogger("BaseGPT")

class ToolCallRecord:
    index: int
    id: str
    name: str
    arguments: str
    result: str
    errors: bool
    
    def __init__(self, index: int, id: str, name: str, arguments: str) -> None:
        self.index = index
        self.id = id
        self.name = name
        self.arguments = arguments
        self.result = "Success"
        self.errors = False

class BaseGPT(BaseModel):
    client: AsyncOpenAI
    model_name: str
    
    def __init__(self, model_name: str) -> None:
        api_key = get_openai_key()
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = model_name 
    
    async def get_streaming_response(
        self, 
        prompt: BasePrompt
    ) -> AsyncGenerator[Tuple[CompletionChunk, bool], None]:
        responses: List[BaseChatResponse] = []
        
        # Create an initial message list based on the prompt, this may be added to later
        messages = [
            msg
            for message in prompt.messages
            for msg in self.get_messages(message)
        ]
        
        if prompt.system_prompt:
            messages.insert(0, ChatCompletionSystemMessageParam(role="system", content=prompt.system_prompt))
        
        # Create the list of tools
        if prompt.tool_choice_filter:
            available_tools = [
                self.get_tool(tool)
                for tool in prompt.tools
                if tool.name in prompt.tool_choice_filter
            ]
        else:    
            available_tools = [self.get_tool(tool) for tool in prompt.tools]
        
        # Loops until there are no more tool calls to process
        while True:
            if available_tools:
                if prompt.forced_tool_name:
                    tool_choice = ChatCompletionNamedToolChoiceParam(
                        type="function",
                        function=NamedToolFunction(
                            name=prompt.forced_tool_name
                        )
                    )
                    
                    response = await self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        tools=available_tools,
                        tool_choice=tool_choice,
                        stream=True
                    )
                elif prompt.tool_choice_filter:
                    response = await self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        tools=available_tools,
                        tool_choice="required",
                        stream=True
                    )
                else:    
                    response = await self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        tools=available_tools,
                        stream=True
                    )
            else:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    stream=True
                )
            
            response_content: str = ""
            tool_call_dict: List[ToolCallRecord] = []
            finish_reason: Literal['stop', 'length', 'tool_calls', 'content_filter', 'function_call']
            
            # Iterate through the completion stream
            # Yield text content as it is received
            # Collect tool calls as they populate
            async for chunk in response:
                tool_calls = chunk.choices[0].delta.tool_calls
                content = chunk.choices[0].delta.content
                    
                if available_tools and tool_calls:
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
                         
                if content:
                    response_content += content
                
                if content or len(tool_call_dict) > 0:
                    yield CompletionChunk.model_construct(
                        message_id=chunk.id,
                        text=content,
                        tools=[
                            Tool.model_construct(
                                name=record.name,
                                data=record.arguments
                            )
                            for record in tool_call_dict
                            if prompt.is_tool_public(record.name)
                        ]
                    ), False
                            
                if chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason
                    logger.info(f"Finish reason: {finish_reason}")
                    break
            
            # Execute any tools that were called
            if len(tool_call_dict) > 0:
                for record in tool_call_dict:
                    logging.info(f"Processing tool: {record.name}")
                    logging.info(record.arguments)

                    # Try to load the JSON - if it fails, return an error to the model for correction
                    try:
                        json_dict = json.loads(record.arguments)
                        record.result = prompt.process_tool(tool_name=record.name, arguments=json_dict)
                    except json.JSONDecodeError:
                        logging.error(f"Error decoding JSON: {record.arguments}")
                        record.result = "Invalid JSON provided to tool"
                        record.errors = True
                    except ValueError as e:
                        logging.error(f"Error processing tool, invalid argument schema: {record.name}: {e}")
                        record.result = f"""{e}
Correct the errors in tool arguments and try again.
"""
                        record.errors = True
                    except Exception as e:
                        logging.error(f"Error processing tool, unhandled error: {record.name}: {e}")
                        record.result = f"Error: {e}"
                        record.errors = True
            
            responses.append(
                BaseChatResponse(
                    message=response_content, 
                    tool_calls=[
                        BaseToolCallWithResult(
                            id=record.id,
                            name=record.name, 
                            arguments=record.arguments,
                            result=record.result
                        ) for record in tool_call_dict
                    ]
                )
            )
            
            # If the finish reason is tool calls, added to the chat context and repeat the loop
            if finish_reason == "tool_calls" or len(tool_call_dict) > 0:
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
                
                messages.append(response_message)
                
                for record in tool_call_dict:
                    messages.append(ChatCompletionToolMessageParam(
                        role="tool", 
                        tool_call_id=record.id, 
                        content=record.result
                    ))
                    
                # If the model was forced to call this a tool, break the loop unless there are errors
                if prompt.forced_tool_name and not any(record.errors for record in tool_call_dict):
                    break
            else:
                break

            # The final yield includes the responses
            yield CompletionChunk.model_construct(), responses
        
    def get_messages(
        self, 
        message: BaseChatMessage
    ) -> List[ChatCompletionMessageParam]:
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
                
                return [
                    ChatCompletionUserMessageParam(
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
                ]
                
            return [
                ChatCompletionUserMessageParam(
                    role="user", 
                    content=message.message
                )
            ]
        elif message.role == ChatRole.AGENT:
            return [
                ChatCompletionAssistantMessageParam(
                    role="assistant", 
                    content=message.message,
                    tool_calls=[
                        ChatCompletionMessageToolCall(
                            type="function",
                            id=tool_call.id,
                            function=FunctionCall(
                                name=tool_call.name,
                                arguments=json.dumps(tool_call.arguments)
                            )
                        )
                        for tool_call in message.tool_calls
                    ] if message.tool_calls else None
                ),
                *[
                    ChatCompletionToolMessageParam(
                        role="tool",
                        tool_call_id=tool_call.id,
                        content=tool_call.result
                    )
                    for tool_call in message.tool_calls
                ]
            ]
        elif message.role == ChatRole.TOOL:
            return [
                ChatCompletionToolMessageParam(
                    role="tool", 
                    content=message.message
                )
            ]
        else:
            raise ValueError(f"Unknown message role: {message.role}")
        
    def get_tool(self, tool: BaseTool) -> dict:
        return ChatCompletionToolParam(
            type="function",
            function=FunctionDefinition(
                name=tool.name,
                description=tool.description,
                parameters=tool.schema
            )
        )