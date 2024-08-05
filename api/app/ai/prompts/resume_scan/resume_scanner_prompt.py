from typing import List
from .. import BasePrompt
from .provide_profile_tool import ProvideProfileTool

class ResumeScannerPrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You will look through imag(es) of a resume and extract information from it.
The information you will look for is denoted in the schema of the provide_profile tool.
You will use the provide_profile tool to send your results back to the user.

When filling out the bio, you will make it less formal (as in a resume format) and more casual (as in a bio format, first person).
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