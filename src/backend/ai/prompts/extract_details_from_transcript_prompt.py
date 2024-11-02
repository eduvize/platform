from typing import List
from ai.prompts.base_prompt import BasePrompt
from ai.common.base_message import BaseChatMessage

class ExtractDetailsFromTranscriptPrompt(BasePrompt):
    def setup(self) -> None:
        pass
    
    async def get_extracted_details(self, history: List[BaseChatMessage], instructions: str) -> str:
        from ai.models.gpt_4o import GPT4o
        model = GPT4o()
        
        self.set_system_prompt(f"""
You will extract specific information from the current chat conversation.
You will structure your output according to the instructions provided, and only provide the requested details.
You will observe messages from the user and assistant, as well as tool arguments that have been provided in each message.
""".strip())
        self.add_history(history)
        self.add_user_message(instructions)
        
        responses = await model.get_responses(self)
        
        return responses[0].message