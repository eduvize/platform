import logging
import json
import base64
import asyncio
from typing import AsyncGenerator, List, Literal, Tuple, Any

from . import BaseModel
from domain.dto.ai.completion_chunk import CompletionChunk, Tool
from typing import AsyncGenerator, List, Literal, Tuple
from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionAssistantMessageParam, 
    ChatCompletionUserMessageParam, 
    ChatCompletionToolMessageParam, 
    ChatCompletionToolParam, 
    ChatCompletionContentPartTextParam,
    ChatCompletionContentPartImageParam,
    ChatCompletionMessageToolCall, 
    ChatCompletionMessageParam,
)
from openai.types.chat.chat_completion_named_tool_choice_param import Function as NamedToolFunction, ChatCompletionNamedToolChoiceParam
from openai.types.chat.chat_completion_content_part_image_param import ImageURL
from openai.types.shared import FunctionDefinition
from config import get_openai_key
from ai.prompts import BasePrompt
from ai.common import BaseChatMessage, BaseChatResponse, BaseTool, BaseToolCallWithResult, ChatRole
from ai.util.tool_decorator import TOOL_REGISTRY, ToolWrapper

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
    available_tools: List[BaseTool]
    
    def __init__(self, model_name: str) -> None:
        api_key = get_openai_key()
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = model_name
    
    async def get_streaming_response(
        self, 
        prompt: BasePrompt
    ) -> AsyncGenerator[Tuple[CompletionChunk, list[BaseChatResponse], bool], None]:
        responses: List[BaseChatResponse] = []
        
        # Create an initial message list based on the prompt, this may be added to later
        messages = [
            msg
            for message in prompt.messages
            for msg in self.get_messages(message)
        ]
        
        if prompt.system_prompt:
            messages.insert(0, ChatCompletionSystemMessageParam(role="system", content=prompt.system_prompt))
        
        self.available_tools = [
            tool for key, tool in TOOL_REGISTRY.items()
            if key.startswith(f"{prompt.__module__}.")
        ]
        
        # Loops until there are no more tool calls to process
        while True:
            # Create the list of tools
            forced_tools = []
            tools_to_use = []
            tool_use_mode: Literal["required", "auto"] = "auto"
            
            for tool in self.available_tools:
                if tool.force_if and tool.force_if(prompt):
                    forced_tools.append(self.get_tool(tool))
                elif not tool.force_if:
                    tools_to_use.append(self.get_tool(tool))
            
            if len(forced_tools) > 0:
                logger.info(f"Forcing tools: {forced_tools}")
                tools_to_use = forced_tools
                tool_use_mode = "required"
            else:
                logger.info("No forced tools")
            
            if tools_to_use:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=tools_to_use,
                    tool_choice=tool_use_mode,
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
                    
                if tools_to_use and tool_calls:
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
                            if TOOL_REGISTRY[f"{prompt.__module__}.{record.name}"].is_public  # Only include public tools in the chunk
                        ]
                    ), [], False
                            
                if chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason
                    logger.info(f"Finish reason: {finish_reason}")
                    break
            
            # Execute any tools that were called
            if len(tool_call_dict) > 0:
                tool_tasks = []
                for record in tool_call_dict:
                    # Try to load the JSON - if it fails, return an error to the model for correction
                    try:
                        logging.info(f"Executing tool: {record.name} with arguments: {record.arguments}")
                        json_dict = json.loads(record.arguments)
                        tool_tasks.append(self.execute_tool(prompt, record.name, json_dict))
                    except json.JSONDecodeError:
                        logger.error(f"Error decoding JSON: {record.arguments}")
                        record.result = "Invalid JSON provided to tool"
                        record.errors = True
                    except ValueError as e:
                        logger.error(f"Error processing tool, invalid argument schema: {record.name}: {e}")
                        record.result = f"{e}\nCorrect the errors in tool arguments and try again."
                        record.errors = True
                    except Exception as e:
                        logger.error(f"Error processing tool, unhandled error: {record.name}: {e}")
                        record.result = f"Error: {e}"
                        record.errors = True

                # Wait for all tool executions to complete
                tool_results = await asyncio.gather(*tool_tasks, return_exceptions=True)
                
                for record, result in zip(tool_call_dict, tool_results):
                    logging.info(f"Collecting result for {record.name}")
                    if isinstance(result, Exception):
                        logging.error(f"Error executing tool: {record.name}: {result}")
                        record.result = f"Error: {result}"
                        record.errors = True
                    else:
                        logging.info(f"Tool {record.name} completed successfully")
                        record.result = result

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
                            function=NamedToolFunction(
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
                if tool_use_mode == "required" and not any(record.errors for record in tool_call_dict):
                    break
            else:
                break

        # The final yield includes the responses
        yield CompletionChunk.model_construct(), responses, True
        
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
                            function=NamedToolFunction(
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

    async def execute_tool(self, prompt: BasePrompt, tool_name: str, arguments: dict) -> Any:
        tool_key = f"{prompt.__module__}.{tool_name}"
        if tool_key not in TOOL_REGISTRY:
            raise ValueError(f"Unknown tool: {tool_name}")
        tool = TOOL_REGISTRY[tool_key]
        return await tool.process(prompt, arguments)
