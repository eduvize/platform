from typing import Generator, List, Tuple
from ai.prompts import BasePrompt
from ai.common import BaseChatMessage, BaseChatResponse, ChatRole

class CoursePlanningPrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You are an instructor who will speak encouragingly to a student who is working with you to develop course plans.                       
""")

    def get_response(self, profile_text: str, history: List[BaseChatMessage], message: str) -> Generator[Tuple[str, str], None, List[BaseChatResponse]]:
        from ...models.gpt_4o_mini import GPT4oMini
        
        self.add_agent_message(f"""
I've pulled the profile information for the student. Here is what I have:
{profile_text}                           
""")
        
        for hist in history:
            if hist.role == ChatRole.USER:
                self.add_user_message(message=hist.message)
            else:
                self.add_agent_message(message=hist.message)
        
        self.add_user_message(message)

        model = GPT4oMini()
        text_stream = model.get_streaming_response(self)
        
        while True:
            try:
                yield next(text_stream)
            except StopIteration as e:
                return e.value