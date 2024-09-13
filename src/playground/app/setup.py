import os
import pty
import select
import subprocess
import requests
import logging
import time
from typing import Callable, Literal, Optional, List
from pydantic import BaseModel
from .config import get_backend_api_endpoint, get_session_id, get_jwt_signing_key
from .jwt import create_token

class SetupStep(BaseModel):
    step_type: Literal["shell_command", "write_file"]
    summary_text: str
    command_str: Optional[str] = None
    file_path: Optional[str] = None
    file_contents: Optional[str] = None

class EnvironmentSetupInstructions(BaseModel):
    steps: List[SetupStep] = []
    

class EnvironmentSetupErrorDto(BaseModel):
    output: str
    instructions: EnvironmentSetupInstructions

def get_setup_instructions() -> EnvironmentSetupInstructions:
    token = create_token(
        data={
            "session_id": get_session_id(),
        },
        secret=get_jwt_signing_key(),
        expiration_minutes=5
    )
    
    response = requests.get(
        f"{get_backend_api_endpoint()}/playground/instance/setup",
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=30  # Optional: set a timeout for the request
    )
    response.raise_for_status()

    return EnvironmentSetupInstructions.model_validate(response.json())

def get_revised_setup_instructions(instructions: EnvironmentSetupInstructions, output: str) -> EnvironmentSetupInstructions:
    token = create_token(
        data={
            "session_id": get_session_id(),
        },
        secret=get_jwt_signing_key(),
        expiration_minutes=5
    )
    
    response = requests.post(
        url=f"{get_backend_api_endpoint()}/playground/instance/setup/revision",
        data=EnvironmentSetupErrorDto.model_construct(output=output, instructions=instructions).model_dump_json(),
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=30  # Optional: set a timeout for the request
    )
    response.raise_for_status()

    return EnvironmentSetupInstructions.model_validate(response.json())

def send_command(command: str) -> tuple[str, str, Optional[int]]:
    """
    Executes the given command in a new pseudo-terminal and returns the output, error, and exit code.
    """
    logging.info(f"Sending command: {command}")

    stdout_lines = []
    stderr_lines = []
    exit_code = None

    def read_output(fd):
        while True:
            try:
                output = os.read(fd, 1024).decode()
                logging.info(output)
                if output:
                    stdout_lines.append(output)
            except OSError:
                break

    pid, fd = pty.fork()

    if pid == 0:
        # Chroot into /userland
        os.chroot("/userland")

        # Change to the user's home directory inside chroot
        os.chdir("/home/user")

        # Set environment variables
        os.putenv("HOME", "/home/user")
        os.putenv("DEBIAN_FRONTEND", "noninteractive")

        # Replace the current process with the command to run inside the chroot
        os.execvp("/bin/bash", ["/bin/bash", "-c", command])
    else:
        # Parent process: Read output and wait for the command to complete
        while True:
            rlist, _, _ = select.select([fd], [], [], 0.1)
            if rlist:
                read_output(fd)
            try:
                # Poll for child process termination
                pid_exit, status = os.waitpid(pid, os.WNOHANG)
                if pid_exit == pid:
                    # Child has exited, break the loop
                    exit_code = os.WEXITSTATUS(status)
                    break
            except ChildProcessError:
                break

        os.close(fd)

    return "".join(stdout_lines), "".join(stderr_lines), exit_code

def rewrite_permissions():
    """
    Provide full ownership and permissions to the user after each step.
    """
    send_command("chown -R user:user /home/user")
    send_command("chmod -R 777 /home/user")
    send_command("chmod -R 777 /root")

def execute_environment_setup(callback: Callable[[str], None]) -> None:
    """
    Gets the environment setup instructions from the backend with retry mechanism.
    Tracks successful steps and revises setup instructions in case of failure.
    """

    max_retries = 3
    backoff_seconds = 3

    # Retry mechanism for the request to /playground/instance/setup
    for attempt in range(1, max_retries + 1):
        try:
            instructions = get_setup_instructions()
            break  # Exit the loop if the request is successful
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                logging.error(f"Failed to get setup instructions after {max_retries} attempts.")
                raise  # Re-raise the exception after the final attempt
            else:
                logging.warning(f"Attempt {attempt} failed with error: {e}. Retrying in {backoff_seconds} seconds...")
                time.sleep(backoff_seconds)

    if not instructions:
        logging.error("No setup instructions received from the backend.")
        return

    logging.info("Executing environment setup instructions")

    while True:
        logging.info(f"Starting environment setup loop with {len(instructions.steps)} steps")
        
        successful_steps = []
        failed_output = ""
        
        try:
            send_command("export DEBIAN_FRONTEND=noninteractive")
            send_command("export HOME=/home/user")
            
            # Execute setup steps
            for step in instructions.steps:
                logging.info(f"Executing step: {step.summary_text}")
                callback(step.summary_text)
                
                if step.step_type == "shell_command":
                    logging.info(f"Executing command: {step.command_str}")
                    stdout, stderr, exit_code = send_command(f"{step.command_str}")

                    if exit_code is not None and exit_code != 0:
                        failed_output = f"Step failed: {step.summary_text}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                        raise subprocess.CalledProcessError(exit_code, step.command_str)

                    successful_steps.append(step.summary_text)

                elif step.step_type == "write_file":
                    logging.info(f"Writing file: {step.file_path}")
                    full_path = os.path.join("/userland", step.file_path.lstrip("/"))
                    dir_path = os.path.dirname(step.file_path)
                    full_dir_path = os.path.join("/userland", dir_path.lstrip("/"))

                    # Ensure directory exists
                    os.makedirs(full_dir_path, exist_ok=True)
                    
                    # Write the file
                    with open(full_path, "w") as f:
                        f.write(step.file_contents)

                    successful_steps.append(step.summary_text)

                rewrite_permissions()
                
        except subprocess.CalledProcessError as e:
            logging.error(f"Environment setup failed at step: {e.cmd}. Exit code: {e.returncode}")

            # Call the revision function with details of successful steps and failed output
            output = f"Successful steps:\n" + "\n".join(successful_steps) + f"\n\nFailed Step Output:\n{failed_output}"
            logging.info(output)
            instructions = get_revised_setup_instructions(instructions, output)

            # Optionally, you could retry with revised instructions here
            logging.info("Revised setup instructions obtained. Retrying...")
            continue
        
        break

    logging.info("Environment setup complete")
