from typing import List
from .provide_options_tool import ProvideOptionsTool
from ai.prompts import BasePrompt

class AutocompletePrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You will generate a list of up to 5 autocompletion options for the subject provided by the user.
You will keep your options strictly to those that start with the provided query and will only include terms used popularly in the software dev industry.
It is okay to provide less than 5 options if you cannot think of more. If the query doesn't match anything you know about, you can provide an empty list.
If there is an exact match, you will make sure you provide it as the first option.
""")
        
        self.use_tool(ProvideOptionsTool)
        
    def get_options(self) -> List[str]:
        from ...models.gpt_4o_mini import GPT4oMini
        
        model = GPT4oMini()
        model.get_responses(self)
        calls = self.get_tool_calls(ProvideOptionsTool)
        
        if not calls:
            return []
        
        return calls[-1].result