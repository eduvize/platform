import logging
from ai.prompts import BasePrompt
from .provide_instructions_tool import ProvideInstructionsTool
from domain.dto.playground.environment_setup_instructions import EnvironmentSetupInstructions

class PlaygroundSetupRevisionPrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You are a diligent staff engineer who specializes in setting up development environments for your software engineers.
You will be working in an Ubuntu Jammy environment hosted within a docker container with full root access, so there is no need to sudo any commands.

The user is running setup instructions that you have provided to them. They are having an issue getting the environment stood up and are providing you
with the following information:
- The environment they were required to set up
- The setup instructions you gave them
- The standard output of the commands they ran, including any errors

You will provide an updated set of instructions to help them get the environment set up correctly.

Keep in mind, the current working directory is reset after each step - so any shell commands you run will need to be self-contained.
Commands are expected to be non-interactive and should not require any user input.
""".strip())
        
    async def get_setup_spec(self, instructions: EnvironmentSetupInstructions, scenario: str, info: str) -> EnvironmentSetupInstructions:
        from ai.models.gpt_4o import GPT4o
        model = GPT4o()
        
        self.add_user_message(f"""
What I need:
{scenario}

Your previous instructions:
{instructions.model_dump_json(indent=4)}

{info}
""".strip())

        self.use_tool(ProvideInstructionsTool, force=True)
        await model.get_responses(self)
        instructions_call = self.get_tool_call(ProvideInstructionsTool)
        
        if not instructions_call.result:
            raise Exception("Failed to get setup spec")
        
        logging.info(instructions_call.result.model_dump_json(indent=4))
        return instructions_call.result