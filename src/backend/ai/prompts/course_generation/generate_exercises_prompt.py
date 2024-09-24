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
Each exercise will have a specific mock scenario that the user will be asked to complete.

An exercise consists of:
- Detailed summary: A comprehensive plan that describes the full exercise in detail, including reasons how the exercise will help the user learn from the lesson
- A title: A friendly title that describes the mock scenario of the exercise
- Initial environment state: A comprehensively detailed description of the initial state of the development environment that is expected for the user to be able to start the exercise
- Objectives: A list of code-based objectives that the user should be able to complete by the end of the exercise
- Docker image: A Docker Hub image to use as the base for the development environment, use the 'ubuntu:jammy' image if unsure. Preference for language-specific images.

Objectives:
The objective should be a verifiable task that the user can complete by writing code, running specific commands, or by making changes to the codebase.
Each objective must include a test plan that the instructor can read to understand how to verify that the objective has been completed successfully.

Example Exercises:
Exercise Example 1:
Title: Create a Basic Function in JavaScript
Summary: Write a function that takes two numbers as arguments and returns their sum
Exercise Example 2:
Title: Define a Class in Python
Summary: Create a class called Person with attributes for name and date of birth with a method to calculate the age 
Exercise Example 3:
Title: Incorporate a New API Endpoint
Summary: Add a new GET endpoint to the API that returns a list of users using fake data

Example objectives with their test plans:
Objective 1: Write a function that returns the sum of two numbers
Test plan 1: Read example.rs and verify that there is a function that returns the sum of two provided numbers
Objective 2: Create a class that represents a person
Test plan 2: Read person.py and verify that there is a class that represents a person with relevant attributes and methods
Objective 3: Incorporate a new GET endpoint into the API
Test plan 3: Examine the codebase and verify there is a defined GET endpoint. Run the development server and make a GET request to the new endpoint, verifying that it responds with a 200 status code

An exercise must incorporate only the following:
- Writing code: The user is instructed to write specific pieces of code
- Running code: The user is instructed to run a program or script
- Reviewing code: The user is instructed to read and understand code
- Debugging code: The user is instructed to find and fix issues in code
- Using the command line: The user is instructed to run specific commands in the terminal

Rules for exercise environments:
- DO NOT attempt to install Docker or require its usage during the exercise. Docker is not allowed in this exercise.

Initial Environment State:
- Tools, libraries or dependencies that will be needed for the user to run the code
- Files that should be pre-populated on the filesystem (i.e classes, functions, etc)
- Configuration files that should be pre-populated on the filesystem (i.e. package.json, requirements.txt, etc)

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