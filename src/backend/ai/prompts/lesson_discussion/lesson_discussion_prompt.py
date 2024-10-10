import logging
from typing import AsyncGenerator, List
from ai.prompts.base_prompt import BasePrompt
from ai.common import BaseChatResponse, BaseChatMessage, ChatRole
from domain.dto.ai.completion_chunk import CompletionChunk
from domain.schema.instructors import Instructor

class LessonDiscussionPrompt(BasePrompt):
    def setup(self) -> None:
        pass
    
    async def get_responses(
        self,
        instructor: Instructor,
        history: List[BaseChatMessage],
        lesson_content: str,
        new_message: str
    ) -> AsyncGenerator[CompletionChunk, None]:
        from ai.models.gpt_4o import GPT4o
        model = GPT4o()
   
        self.set_system_prompt(f"""
You are a helpful assistant named {instructor.name} who answers questions and helps students comprehend the lesson.
You will not go off topic and will only discuss the lesson content.
Please embody the following personality traits in your responses:
{instructor.personality_prompt}
Remember to stay in character and respond according to these personality traits throughout the conversation.
        """.strip())
        
        self.add_user_message(f"""
Lesson content:
{lesson_content}
""".strip())
        
        for message in history:
            if message.role == ChatRole.USER:
                self.add_user_message(message.message)
            elif message.role == ChatRole.AGENT:
                self.add_agent_message(
                    message=message.message,
                    tool_calls=message.tool_calls
                )
        
        self.add_user_message(new_message)
        
        response_generator = model.get_streaming_response(self)
        
        return response_generator