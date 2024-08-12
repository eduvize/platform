from typing import Tuple
from ai.prompts import BasePrompt
from .models import AssertionResult
from .provide_assertion_tool import ProvideAssertionTool


class AssertionPrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You will determine whether or not the given statement is true or false.
You will be objective and sound in your decision and will not consider unreasonable or irrelevant factors.""")
        
        self.use_tool(ProvideAssertionTool)
        
    def get_assertion(self, statement: str) -> Tuple[bool, str]:
        """
        Determine whether or not the given statement is true or false.

        Args:
            statement (str): The statement to evaluate

        Returns:
            (bool, str): The assertion and the reason for the assertion
        """
        from ...models.gpt_4o_mini import GPT4oMini
        
        self.add_user_message(f"""Is this statement true or false?
{statement}""")

        model = GPT4oMini()
        model.get_responses(self)
        
        calls = self.get_tool_calls(ProvideAssertionTool)
        
        if not calls:
            return False
        
        result: AssertionResult = calls[-1].result
        
        return result.assertion, result.reason