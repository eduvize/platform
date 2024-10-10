import logging
from typing import AsyncGenerator, List, Tuple
from ai.prompts import BasePrompt
from ai.common import BaseChatMessage, BaseChatResponse, BaseTool
from domain.dto.ai import CompletionChunk

class BaseModel:
    async def get_responses(self, prompt: BasePrompt) -> List[BaseChatResponse]:
        """
        Performs a streaming request to the AI model and returns the final response asynchronously

        Args:
            prompt (BasePrompt): The prompt to send to the AI model

        Returns:
            List[BaseChatResponse]: The final response from the AI model

        Raises:
            Exception: If an unexpected error occurs during the streaming process
        """
        try:
            async for _, responses, is_final in self.get_streaming_response(prompt):
                if is_final:
                    return responses
        except Exception as e:
            # Log the unexpected error
            logging.error(f"Unexpected error in get_responses: {str(e)}")
            raise

    async def get_streaming_response(self, prompt: BasePrompt) -> AsyncGenerator[Tuple[CompletionChunk, list[BaseChatResponse], bool], None]:
        """
        Performs a streaming request to the AI model and returns the response as an async generator

        Args:
            prompt (BasePrompt): The prompt to send to the AI model

        Yields:
            Tuple[CompletionChunk, bool]: Metadata about the completion chunk and a boolean indicating if it's the final chunk
            
        Returns:
            None
        """
        raise NotImplementedError("Method not implemented")
    
    def get_message(self, message: BaseChatMessage) -> dict:
        raise NotImplementedError("Method not implemented")

    def get_tool(self, tool: BaseTool) -> dict:
        raise NotImplementedError("Method not implemented")