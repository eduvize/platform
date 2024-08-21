import logging
from typing import Generator, List, Tuple
from ai.prompts import BasePrompt
from ai.common import BaseChatMessage, BaseChatResponse, ChatRole
from .provide_course_outline import ProvideCourseOutlineTool
from domain.dto.ai import CompletionChunk

class CoursePlanningPrompt(BasePrompt):
    def setup(self) -> None:
        self.use_tool(ProvideCourseOutlineTool)

    def get_response(
        self,
        instructor_name: str,
        profile_text: str, 
        history: List[BaseChatMessage], 
        message: str
    ) -> Generator[CompletionChunk, None, List[BaseChatResponse]]:
        from ai.models.gpt_4o import GPT4o
        
        self.set_system_prompt(f"""
You are {instructor_name}, a friendly and insightful online learning course instructor.
You will leverage the user's profile information to help them plan a learning course of their choice.
Before submitting the course outline, you will make sure that you have all the necessary details.
You will iteratively work with the user to understand their learning goals and preferences for the course.

You will use your provide_course_outline tool to show the user what you currently have planned as you iterate. You will not include the course outline or an overview in your response, rather you will direct them to the UI.
Examples include:
- "I've updated the course outline. Please check the UI for the details."
- "I've made some changes to the course outline. Please review the UI for the latest updates."
""")

        self.add_agent_message(f"""
I've pulled the profile information for the student. Here is what I have:
{profile_text}""")
        
        self.add_agent_message("I'll wait to see what the user would like to learn and guide them through appropriate topics step-by-step. Afterwards, I'll let them confirm the details before providing a comprehensive outline in natural language.")
        
        for hist in history:
            if hist.role == ChatRole.USER:
                self.add_user_message(message=hist.message)
            else:
                self.add_agent_message(message=hist.message)
        
        self.add_user_message(message)

        model = GPT4o()
        chunk_generator = model.get_streaming_response(self)
        
        while True:
            try:
                yield next(chunk_generator)
            except StopIteration as e:
                return e.value