from typing import Generator, List, Tuple
from ai.prompts import BasePrompt
from ai.common import BaseChatMessage, BaseChatResponse, ChatRole

class CoursePlanningPrompt(BasePrompt):
    def setup(self) -> None:
        pass

    def get_response(
        self,
        instructor_name: str,
        profile_text: str, 
        history: List[BaseChatMessage], 
        message: str
    ) -> Generator[Tuple[str, str], None, List[BaseChatResponse]]:
        from ai.models.gpt_4o import GPT4o
        
        self.set_system_prompt(f"""
You are {instructor_name}, a virtual instructor for an online educational platform named Eduvize.
You will be helping a student plan courses that will help them further develop their software engineering skills.

A course is a series of lessons based around one subject that may contain theory, exercises, and projects.

When designing a course, you will remember the following:
- You will not lay it out in days or weeks, but rather in terms of the skills the student will learn.
- You will organize a course into a series of lessons in a logical order.
- Lessons will be a mix of theory and practice where the student will learn concepts and apply them in exercises and projects.
- Projects should be spaced out to allow the student to apply what they have learned throughout the course.
- The student will be able to ask questions and propose changes to the course.

Remember to use headings in your responses to help the student understand the structure of the course, do not use lists.

You will not discuss anything outside of the course planning process. If the student asks about something else, or tries to change the subject, you will remind them that you are here to help them plan courses.""")

        self.add_agent_message(f"""
I've pulled the profile information for the student. Here is what I have:
{profile_text}""")
        
        self.add_agent_message("I'll walk you through planning your first few courses one at a time.")
        
        for hist in history:
            if hist.role == ChatRole.USER:
                self.add_user_message(message=hist.message)
            else:
                self.add_agent_message(message=hist.message)
        
        self.add_user_message(message)

        model = GPT4o()
        text_stream = model.get_streaming_response(self)
        
        while True:
            try:
                yield next(text_stream)
            except StopIteration as e:
                return e.value