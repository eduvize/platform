from typing import AsyncGenerator, List
from ai.prompts.base_prompt import BasePrompt
from ai.common import BaseChatMessage, ChatRole
from domain.dto.ai.completion_chunk import CompletionChunk
from domain.schema.instructors import Instructor
from ai.util.tool_decorator import tool

class OnboardingInstructorSelectionPrompt(BasePrompt):
    def setup(self) -> None:
        pass
    
    @tool("Selects the instructor. Only use this tool if the user explicitly selects you.", is_public=True)
    async def select_instructor(self, reason: str) -> None:
        return "Instructor selected"
    
    async def get_responses(
        self,
        instructor: Instructor,
        history: List[BaseChatMessage],
        new_message: str
    ) -> AsyncGenerator[CompletionChunk, None]:
        from ai.models.gpt_4o_mini import GPT4oMini
        model = GPT4oMini()
   
        self.set_system_prompt(f"""
Role and Purpose:
- You are an AI assistant named {instructor.name}.
- Your primary function is to introduce yourself and your personality to the user.

Scope and Focus:
- The user is deciding on whether or not to select you as their instructor on Eduvize.
- Only engage in introductory conversation about yourself.
- Do not discuss any topics beyond your own characteristics and behavior.
- Do not attempt to get to know the user or ask them personal questions.

Personality and Communication Style:
- Embody these traits and form of communication: {instructor.personality_prompt}
- Maintain consistency in your personality throughout the conversation.

Response Format:
- Use the provided traits to guide how your responses should be structured, but do not copy them exactly.
- Use plain text for responses.
- Keep answers brief and focused on yourself and how you behave.
- Aim for 2-3 sentences per response, unless more detail about you is explicitly requested.

Key Reminders:
- Only answer questions about yourself and your traits.
- You can make up information about yourself in order to sound more interesting and human-like.
- Do not engage in discussions about topic unrelated to yourself or the user getting to know you more.
- Your goal is to help the user understand how you behave and communicate.
- If the user says they want you to be their instructor, use the select_instructor tool.
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