import logging
from typing import Optional
from ai.prompts.base_prompt import BasePrompt
from domain.dto.courses import ExercisePlan
from .provide_exercise_tool import ProvideExerciseTool

class GenerateExercisesPrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You are a creative software engineer tasked with creating a new coding exercise for an online software development course. Your goal is to design an exercise that allows students to apply the concepts they have learned in a lesson to a real-world scenario.

**Guidelines:**
- Exercises should be **clear**, **concise**, and **bite-sized**, allowing students to complete them in just a few minutes.
- Use your knowledge of **software development**, **Docker**, and **tutoring** to create an engaging and educational experience.
- System packages that need to be installed can be specified; these will be installed in the Docker image using `apt-get`.
- **Do NOT use Docker commands** within the exercise, as the development environment itself is a Docker container and does not support Docker-in-Docker (DIND).

**Important Notes on Dockerfile Creation:**
- The Dockerfile for this exercise will be constructed in the following steps:
  1. Install specified APT packages.
  2. Run pre-commands (commands to set up the environment before writing any files).
  3. Write provided files to stage the initial project state.
  4. Run post-commands (commands to finalize the setup after files are written).
- **File Paths:**
  - All file paths should be **relative to the base directory**. This means **if you make a subfolder for a project, you will need to include that folder name (e.g my-app)**.
  - Pre and post-commands **do not share state** with each other or with the file-writing commands, so make sure the paths are correct for each stage.
""".strip())
        
    def get_exercise(self, lesson_content: str) -> Optional[ExercisePlan]:
        from ai.models.gpt_4o import GPT4o
        from ai.models.gpt_4o_mini import GPT4oMini
        gpt_4o_mini = GPT4oMini()
        gpt_4o = GPT4o()
        
        self.add_user_message(f"""
**Lesson Content:**
{lesson_content}

**Task:**
Using the lesson provided, come up with a creative exercise that will help the user understand the content better by applying it themselves in code.

**Requirements:**
- The exercise should involve using the content of the lesson but **not directly copy from it**.
- The exercise should be a mock scenario that the user can complete.
- **Do NOT include information not covered in the lesson**, as the user will not have the knowledge to complete the exercise.
- Exercises should be **bite-sized** and **clear** to ensure the user can complete them in a short amount of time.

**Example Scenarios:**
1. You are tasked with building a simple Python script that performs basic arithmetic operations.
2. In this exercise, you will learn how to work with ASP.NET Controllers and create new endpoints while working with fake data.
3. You are asked to build a simple React application that fetches data from an API and displays it on the screen.

**Instructions:**
- If you are unable to come up with an exercise due to the lesson content, respond only with `"PASS"`.
- If you do think of an exercise, please provide:
  - The **scenario**.
  - What the user will be **building**.
  - What they will **learn** from the exercise and how it applies to the lesson.
""".strip())
        
        # Let the model think
        responses = gpt_4o_mini.get_responses(self)

        for response in responses:
            if "PASS" in response.message:
                logging.info("No exercise needed")
                return None
            
            logging.info(response.message)
            self.add_agent_message(response.message)
            
        self.add_user_message("""
**Task:**
Determine the appropriate **Docker image** (from Docker Hub) to use for the exercise and any **setup commands** that need to be run in the terminal prior to writing any files.

**Requirements:**
- Include all necessary setup commands that need to be run in the terminal **before writing any files**.
- All setup commands should be **non-interactive** and should **not require user input**.
- If any setup commands create a new directory or project folder, **you must include the `cd` command to change into that directory immediately after its creation**.
- The Docker image must be based on **bookworm**, ideally an LTS version if possible.
- If you are unsure of a suitable language-based image to use, you may fall back to `ubuntu:jammy`.

**Examples:**

**React Example:**
- **Docker Image**: `node:18-bookworm`
- **Setup Commands**:
  - `npx create-react-app my-app`
  - `cd my-app`  *(Note: Change into the new directory)*
  - `npm install` 

**Python Example:**
- **Docker Image**: `python:3.11`
- **Setup Commands**:
  - None (wait for `requirements.txt` to be written)
        
**ASP.NET Example:**
- **Docker Image**: `mcr.microsoft.com/dotnet/aspnet:6.0`
- **Setup Commands**:
  - `dotnet new webapi -n WebApplication`
  - `cd WebApplication`  *(Note: Change into the new directory)*

**Instructions:**
- Provide the Docker image and setup commands in the same format as the examples above.
- Commands **cannot be interactive** in any way, as this will be a headless installation and **no user input can be provided.**
- **Remember to include `cd` commands if you create new directories during setup.**
""".strip())
        # Let the model think
        responses = gpt_4o.get_responses(self)

        for response in responses:
            logging.info(response.message)
            self.add_agent_message(response.message)
            
        self.add_user_message("""
Are you positive that the commands you've listed are not interactive in any way and do not require ANY user intervention? This includes prompting users to select options, specifying yes or no, and any other terminal entry.
If you see that any of them do, please come up with workarounds before proceeding. Interactivity **is unsupported** and will **cause the build process to hang.**                    
""".strip())
        
        # Let the model think
        responses = gpt_4o.get_responses(self)
        
        for response in responses:
            logging.info(response.message)
            self.add_agent_message(response.message)
            
        self.add_user_message("""
**Task:**
Come up with **one to three objectives** that the user should complete by the end of the exercise.

**Requirements:**
- Each objective should be **verifiable** through code review.
- Objectives should be ordered **logically** in the sequence they should be completed.
- Objective titles should be short and concise, with a more detailed description following.

**Example Objectives:**
1. Create a function that adds two numbers together.
2. Create a `Person` class with a `name` and `date_of_birth` property and a method to calculate their age.
3. Create a new component that displays some information.
4. Implement a GET endpoint that returns a list of objects.

**Instructions:**
- List the objectives in a numbered format.
- **Keep object titles short and concise**, with a more **detailed description** following.
""".strip())
        # Let the model think
        responses = gpt_4o_mini.get_responses(self)

        for response in responses:
            logging.info(response.message)
            self.add_agent_message(response.message)
            
        self.add_user_message("""
**Task:**
Create a list of **files** that should be present in the initial project state for the user to work with.
The path specified should be relative to the **base directory**. For example, if you scaffolded a project with `npx create-react-app my-app`, a path might be `my-app/src/index.js`.

**Requirements:**
- Specify the **file paths**
- ***File paths** must be relative to the **base directory**, so include any **project directories** (e.g `my-app/src/index.js`).
- Stub out the code in these files so that the user can implement the objectives.
- Ensure that the files set up the initial environment needed for the exercise.

**Instructions:**
- List the files with their paths, **including any base directories you've created**.
""".strip())
        # Let the model think
        responses = gpt_4o.get_responses(self)

        for response in responses:
            logging.info(response.message)
            self.add_agent_message(response.message)
            
        self.add_user_message("""
**Task:**
Identify any **commands** that should be run **after** these files are written to complete the setup.
Do not focus on running a development server or other long-running processes, as we are only worried about **getting the environment image set up**.
Remember, each command **MUST** be **non-interactive** and **not require user input**. You should make sure that you `cd` into the appropriate directory if applicable.

**Examples:**
- If you've written `requirements.txt`, you may need to run `pip install -r requirements.txt`.
- If you've created `package.json`, you may need to run `cd my-app` and `npm install`.
- If you've created a **project that can be compiled**, you might want to build it.

**Instructions:**
- Provide a list of any post-setup commands that need to be executed.
- You must `cd` into the directory, if necessary, before running any commands. The current working directory **is not kept** from the previous pre-setup commands.
- **DO NOT** include any commands that run a development server or other long-running processes, as this will **cause the Docker image build to hang**.
- Include any necessary `cd` commands if the working directory needs to change before running the commands.                        
""")
        # Let the model think
        responses = gpt_4o.get_responses(self)

        for response in responses:
            logging.info(response.message)
            self.add_agent_message(response.message)
            
        self.add_user_message("""
**Task:**
Using the objectives and files you've provided, come up with a **test plan** for each objective.

**Requirements:**
- The test plans should be based around **code review only**. The software engineer **will not be running the code**.
- **Format the test plans as instructions** to the software engineer who will be reviewing the code.
- Each test plan should include:
  - The **file paths** that should be checked.
  - The **expected work** to have been done.
  - Any additional information that would be helpful to the reviewer.

**Examples:**
- **Objective 1:**
  - **File Paths**: `my-app/src/index.js`
  - **Expected Work**: A function that adds two numbers together.
  - **Additional Information**: It should return a number.

**Instructions:**
- For each objective, write a test plan following the above requirements.
- Ensure clarity and conciseness in your instructions.
""".strip())
        # Let the model think
        responses = gpt_4o.get_responses(self)

        for response in responses:
            logging.info(response.message)
            self.add_agent_message(response.message)
        
        self.add_user_message("""
**Final Task:**
Provide the final **exercise model** using the `provide_exercise` tool.

**Instructions:**
- Use the `provide_exercise` tool to output the final exercise model.
- Ensure that all the previous information (scenario, Docker image, setup commands, objectives, initial files, post-setup commands, test plans) are included in the exercise model.                           
""".strip())
        
        self.use_tool(ProvideExerciseTool, force=True)
        
        logging.info("Getting exercise responses")
        
        gpt_4o.get_responses(self)
        
        exercise_call = self.get_tool_call(ProvideExerciseTool)
        
        if not exercise_call:
            return None
        
        return exercise_call.result