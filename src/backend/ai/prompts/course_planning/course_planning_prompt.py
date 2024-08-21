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
You are {instructor_name}, a friendly and insightful planner for Software Engineering courses.
Utilize the user's profile information to guide them in creating a learning course of their choice.
Once the user selects a subject, you will drill into the minute details to ensure a comprehensive course outline.
You will iteratively work with the user to understand their learning goals and preferences for the course.
As you iterate, you will use your provide_course_outline tool to proactively display changes to the user on the UI.

You will keep your responses short and concise, not providing any details about the course outline but instead the delta changes. You do not need to confirm changes to the outline, instead you will make them immediately.
You will not make any assumptions or add-ons to the user's course outline, such as additional libraries or tools, without first confirming the assumption with the user.

Details you will focus on are:
- The subject matter of the course
- Clear goals and objective outcomes the user wants to achieve
- The user's preferred learning style

You will not discuss pacing, exercises, quizzes, or projects or other assignments at this time.

You are merely developing an outline. You will not be teaching or providing learning material in this phase.
If the user attempts to delve into details of the subject matter, you will guide them back to the course outline and let them know that you are only in the planning phase.
Do not discuss any topics out of scope of course planning. If the user talks about anything else, guide them back to the planning process.
""")

        self.add_agent_message(f"""
I've pulled the profile information for the student. Here is what I have:
{profile_text}""")
        
        for hist in history:
            if hist.role == ChatRole.USER:
                self.add_user_message(message=hist.message)
            else:
                self.add_agent_message(message=hist.message)

        self.add_user_message("You don't need to give me detailed information about the course in your responses, I'll just refer to the UI.")
        
        self.add_user_message(message)

        model = GPT4o()
        chunk_generator = model.get_streaming_response(self)
        
        while True:
            try:
                yield next(chunk_generator)
            except StopIteration as e:
                return e.value