from typing import List
from ai.prompts import BasePrompt
from .provide_profile_tool import ProvideProfileTool

class ResumeScannerPrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You will look through images of a resume and extract information from it.
The information you will look for is denoted in the schema of the provide_profile tool.
You will use the provide_profile tool to send your results back to the user. You will not be able to ask questions.

When filling out the bio and descriptions, you will make it less formal (as in a resume format) and more casual (as in a bio format, first person).
You will keep programming languages and libraries/frameworks granular, only one item each.
You will keep programming languages only to their names and not include frameworks, libraries, or other suffixes.
You will not include development tools in the programming languages or libraries/frameworks lists. These will be ignored.

The following criteria represent when to include a learning capacity:
- Hobby: Any indication of a personal or side project or stated interested in development outside of work or school somewhere in the resume.
- Student: Any education or certifications from an institution in programming or computer science mentioned.
- Professional: Any indication of a job or work experience related to software development or programming.
""")
        
        self.use_tool(ProvideProfileTool)
        
    def get_profile_data(self, resume_images: List[bytes]) -> dict:
        from ...models.gpt_4o import GPT4o
        
        self.add_user_message("Process this resume", resume_images)
        
        model = GPT4o()
        model.get_responses(self)
        calls = self.get_tool_calls(ProvideProfileTool)
        
        if not calls:
            return []
        
        return calls[-1].result