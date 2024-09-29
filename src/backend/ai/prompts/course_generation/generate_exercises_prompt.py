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
- **Detailed Summary**: A comprehensive explanation that describes the exercise in detail to the user, including how the exercise will help the user learn from the lesson
- **Title**: A friendly title that encompasses the scenario in a friendly manner
- **Initial Environment State**:
    - This will be provided to a developer as a starting point for building the development environment and should include all necessary information to set up the exercise project.
    - A comprehensive summary of what project files should be pre-populated in the environment
    - Build tools that should be used to scaffold and run the code
    - Additional tools, libraries, or dependencies that will be needed for the user to run the code
- **Objectives**: 
    - A list of code-based objectives that the user should complete by the end of the exercise
    - Each objective should be verifiable through code review
    - Objectives should be ordered in a way that the user can complete them in a logical sequence
    - Each objective must have a test plan that the instructor can read to understand how to verify that the objective has been completed successfully
    - Each objective should have a description that explains to the user what they need to do to pass the test plan
- **Docker Image**:
    - A suitable base image from Docker Hub that contains the necessary language tooling or libraries for the exercise
    - Use LTS images or images based on bookworm. DO NOT use bullseye, buster, alpine, or slim images.
    - If you are unsure of which image to use, you can use `ubuntu:jammy` as a fallback when necessary, but a language-specific image is preferred

Example Exercise #1:
- **Title**: Add Two Numbers
- **Detailed Summary**: In this exercise, you will write a function that takes two numbers as arguments and returns their sum. This exercise will help you understand how to write basic functions in Python.
- **Initial Environment State**: A virtual environment should be set up. Include a `main.py` file with a bodyless function called `add_numbers` that takes two arguments and a pass statement.
- **Docker Image**: python:3.11

Example Exercise #2:
- **Title**: Create an Endpoint
- **Description**: In this exercise, you will create a new GET endpoint to the API that returns a list of users using fake data. This exercise will help you understand how to create endpoints in ASP.NET Core.
- **Initial Environment State**: An ASP.NET Core project should be set up. Include a blank controller without any endpoints. A `Models` folder should be created with a `User` class that has properties for `Id`, `Name`, and `Email`.
- **Docker Image**: mcr.microsoft.com/dotnet/aspnet:6.0

Example Objectives:
- **Example #1:**
    - **Objective**: Add Two Numbers
    - **Description**: Write a function that takes two numbers as arguments and returns their sum
    - **Test Plan**: Read example.rs and verify that there is a function that returns the sum of two provided numbers
- **Example #2:**
    - **Objective**: Create a Person
    - **Description**: Create a class called Person with attributes for name and date of birth with a method to calculate the age
    - **Test Plan**: Read person.py and verify that there is a class that represents a person with relevant attributes and methods
- **Example #3:**
    - **Objective**: Implement a GET Endpoint
    - **Description**: Add a new GET endpoint to the API that returns a list of users using fake data
    - **Test Plan**: Examine the codebase and verify there is a defined GET endpoint that returns a list of users

An exercise must incorporate only the following:
- Writing code: The user is instructed to write specific pieces of code
- Running code: The user is instructed to run a program or script
- Reviewing code: The user is instructed to read and understand code
- Debugging code: The user is instructed to find and fix issues in code
- Using the command line: The user is instructed to run specific commands in the terminal

Rules for exercise environments:
- DO NOT attempt to install Docker or require its usage during the exercise. Docker is not allowed in this exercise.

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