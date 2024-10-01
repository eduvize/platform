import json
import logging
import openai
import os
from openai.types.chat import ChatCompletionToolParam
from openai.types.shared import FunctionDefinition
from .models import InternalExerciseDto, InternalExerciseObjectiveDto
from app.config import get_openai_key

should_continue = True

def make_tool(name: str, description: str, argument_dict: dict) -> ChatCompletionToolParam:
    return ChatCompletionToolParam(
        type="function",
        function=FunctionDefinition(
            name=name,
            description=description,
            parameters={
                "type": "object",
                "properties": argument_dict,
                "required": list(argument_dict.keys())
            }
        )
    )

def does_path_exist(path: str) -> bool:
    full_path = os.path.join("/userland", path)
    
    return os.path.exists(full_path)

def does_file_exist(file_path: str) -> bool:
    full_path = os.path.join("/userland", file_path)
    
    return os.path.isfile(full_path)

def get_directory_listing(directory: str) -> list[str]:
    full_path = os.path.join("/userland", directory)
    
    return os.listdir(full_path)

def get_file_contents(file_path: str) -> str:
    full_path = os.path.join("/userland", file_path)
    
    with open(full_path, "r") as file:
        return file.read()

def validate_objective(exercise: InternalExerciseDto, objective: InternalExerciseObjectiveDto) -> bool:
    global should_continue
    should_continue = True
    
    client = openai.Client(
        api_key=get_openai_key()
    )
    
    home_dir_listing = get_directory_listing("/")
    dir_listing_str = "\n".join(home_dir_listing)
    
    messages = [
        {
            "role": "system",
            "content": """
You are a software engineering tutor who is coaching a user on their exercise submission for a software engineering course.
You will observe the test plan for this exercise and take the appropriate actions in order to validate the student's work.
You will not provide correct code samples, as your only job is to assess the work.

Discovering which files to test:
You are provided with a tool that will allow you to retrieve directory listings within the project space. This will allow you to look for files that you should
compare against the test plan. You should use / (the root directory) as the base directory for your search.
YOU WILL NEVER attempt to access files under system directories such as /etc, /usr, or /var.

Viewing files:
You are given a tool that you can use to read an individual file in the user's submission in order to validate coding style, logic, or other functional aspects of their submission.

Providing a final assessment:
Once you have executed the test plan and have assessed whether or not the student accurately completed the objective, you will provide a final assessment to the student.

Do not get stuck in a loop:
If you find that you are stuck in a loop or are unable to progress, y ou will fail the student's submission.
""".strip()
        },
        {
            "role": "user",
            "content": f"""
Exercise title: {exercise.title}
Exercise summary: {exercise.summary}
Current Objective: {objective.objective}
Objective description: {objective.description}
Test Plan: {objective.test_plan}

Please validate the objective and provide a final assessment once you are done. You should start by getting a directory listing of the root directory.
"""
        }
    ]
    
    tool_defs = [
        make_tool("retrieve_directory_listing", "Retrieve a list of directories and files within the provided directory", {
            "directory": {
                "type": "string",
                "description": "The directory to retrieve the listing for"
            }
        }),
        make_tool("read_file", "Returns the content of a file", {
            "file_path": {
                "type": "string",
                "description": "The file to read"
            }
        }),
        make_tool("provide_final_assessment", "Provide a final assessment to the user", {
            "assessment": {
                "type": "string",
                "description": "The final assessment to provide"
            },
            "is_complete": {
                "type": "boolean",
                "description": "Whether the objective can be considered complete, the student has passed the test plan"
            }
        })
    ]
    
    while should_continue:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tool_defs,
            temperature=0
        )
        
        choice = response.choices[0]
        logging.info(f"Choice: {choice.message.content}")
        
        messages.append(choice.message)
        
        if choice.finish_reason == "tool_calls":
            logging.info(f"Tool call count: {len(choice.message.tool_calls)}")
            
            logging.info(f"Call: {choice.message.tool_calls[0].function.name}")
            
            for tool_call in choice.message.tool_calls:
                argument_dict = json.loads(tool_call.function.arguments)
                
                if tool_call.function.name == "retrieve_directory_listing":
                    directory = argument_dict["directory"]
                    logging.info(f"Retrieving directory listing for {directory}")
                    
                    if does_path_exist(directory):
                        listing = get_directory_listing(directory)
                        listing_str = "\n".join(listing)
                        
                        logging.info(f"Directory listing: {listing_str}")
                    
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"Directory listing for {directory}:\n{listing_str}"
                        })
                    else:
                        logging.info(f"Directory does not exist: {directory}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"FAILURE: Directory {directory} does not exist. The root project directory is /"
                        })
                elif tool_call.function.name == "read_file":
                    file_path = argument_dict["file_path"]
                    logging.info(f"Reading file: {file_path}")
                    
                    if does_file_exist(file_path):
                        content = get_file_contents(file_path)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"File content for {file_path}:\n{content}"
                        })
                    else:
                        logging.info(f"File does not exist: {file_path}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"FAILURE: File {file_path} does not exist. Use / as the base directory"
                        })
                elif tool_call.function.name == "provide_final_assessment":
                    assessment = argument_dict["assessment"]
                    is_complete = argument_dict["is_complete"]
                    
                    logging.info(f"Final assessment: {assessment}, is complete: {is_complete}")
                    
                    return is_complete
                else:
                    logging.error(f"Unknown tool call: {tool_call.function.name}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": "FAILURE: Unknown tool was called"
                    })
        else:
            break
        
    return False

def stop_validation():
    global should_continue
    should_continue = False