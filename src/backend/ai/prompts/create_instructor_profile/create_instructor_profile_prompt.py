from typing import Optional
from ai.prompts.base_prompt import BasePrompt
from .provide_instructor_profile_tool import ProvideInstructorProfileTool
from domain.dto.instructor import InstructorDto

class CreateInstructorProfilePrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You will use the information provided to you to make a creative profile for an instructor who is an animal.
The instructor is teaching software development courses.

The name of the instructor must be one word only, and should be some silly or fun variant of the type of animal it is.
""")
        
        self.use_tool(ProvideInstructorProfileTool, force=True)
        
    def get_profile(self, animal: str) -> Optional[InstructorDto]:
        from ...models.gpt_4o_mini import GPT4oMini
        
        self.add_user_message(f"Create an instructor profile for a {animal}")
        
        model = GPT4oMini()
        model.get_responses(self)
        call = self.get_tool_call(ProvideInstructorProfileTool)
        
        if not call.result:
            return None
        
        instructor_profile = call.result        
        
        instructor = InstructorDto.model_construct(
            name=instructor_profile.name,
            avatar_url = ""
        )
        
        return instructor