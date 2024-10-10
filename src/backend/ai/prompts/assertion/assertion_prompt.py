from typing import Tuple
from ai.prompts import BasePrompt
from .provide_assertion_tool import ProvideAssertionTool


class AssertionPrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You will determine whether or not the given statement is true or false.
You will be objective and sound in your decision and will not consider unreasonable or irrelevant factors.""")
        
        self.use_tool(ProvideAssertionTool, force=True)
        
    async def get_assertion(self, statement: str) -> Tuple[bool, str]:
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
        await model.get_responses(self)
        
        call = self.get_tool_call(ProvideAssertionTool)
        
        if not call.result:
            return False
        
        return call.result.assertion, call.result.reason