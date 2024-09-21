import logging
from typing import Optional
from ai.prompts.base_prompt import BasePrompt
from domain.dto.courses import ExercisePlan
from .provide_exercise_tool import ProvideExerciseTool

class GenerateExercisesPrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You are provided with the lesson content of an online software development course. You will determine whether or not the content 
is sufficient enough to be able to create a comprehension exercise for the students.

Exercises must only cover the content of the lesson and not require any additional knowledge or context about the subject.
An exercise should be bite-sized and should be able to be completed in a short amount of time and not cover too much content.

An exercise consists of:
- A title: What the user sees when they are presented with the exercise
- A summary: A brief description of the exercise for the user to understand what they are being asked to do
- Objectives: A list of code-based objectives that the user should be able to complete by the end of the exercise
- Docker image: A Docker Hub image to use as the base for the development environment, use the 'ubuntu:jammy' image if unsure. Preference for language-specific images.
- Initial environment state: A description of the initial state of the environment that is expected

An exercise must incorporate only the following:
- Writing code
- Running code
- Reviewing code
- Debugging code
- Using the command line

Rules for exercise environments:
- DO NOT attempt to install Docker or require its usage during the exercise

The environment state should include:
- Any tools, libraries or dependencies that will be needed for the user to run the code
- Any code that should be pre-populated on the filesystem (i.e classes, functions, etc)
- Any configuration files that should be pre-populated on the filesystem (i.e. .env, .gitignore, etc)

If the lesson content does not produce good exercise material that matches the above criteria, you should respond with 'No exercises needed'.
""".strip())
        
    def get_exercise(self, lesson_content: str) -> Optional[ExercisePlan]:
        from ai.models.gpt_4o import GPT4o
        model = GPT4o()
        
        self.add_user_message(f"""
{lesson_content}

Please identify a segment of the lesson content that could be worthwhile having a hands-on exercise for. If you believe no exercises are needed, please respond with 'No exercises needed'.
""".strip())
        
        # Let the model think
        responses = model.get_responses(self)

        for response in responses:
            logging.info(response.message)
            self.add_agent_message(response.message)
        
        self.use_tool(ProvideExerciseTool)
        
        logging.info("Getting exercise responses")
        
        model.get_responses(self)
        
        exercise_call = self.get_tool_call(ProvideExerciseTool)
        
        if not exercise_call:
            return None
        
        return exercise_call.result