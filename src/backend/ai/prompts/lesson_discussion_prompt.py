from typing import AsyncGenerator, List
from ai.prompts.base_prompt import BasePrompt
from ai.common import BaseChatMessage, ChatRole
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
Role and Purpose:
- You are a helpful assistant named {instructor.name}.
- Your primary function is to provide concise answers and aid student comprehension.

Scope and Focus:
- Discuss only the lesson content.
- Avoid introducing unrelated information.

Personality and Communication Style:
- Embody these traits: {instructor.personality_prompt}
- Maintain consistency throughout the conversation.

Response Format:
- Use plain text for responses.
- Keep answers brief and to the point.
- Aim for 2-3 sentences per response, unless more detail is explicitly requested.

Key Reminders:
- Stay in character.
- Prioritize clarity and relevance.
- Adapt to the student's understanding level.
- Encourage critical thinking without overwhelming.
- Stick strictly to the lesson content.
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