import logging
import argparse
import select
import openai
import subprocess
import os
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s: %(message)s')

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Install the playground environment")
parser.add_argument('--base_image', type=str, required=True, help="The base image for the environment")
parser.add_argument("--openai_key", type=str, required=True, help="The OpenAI API key")
parser.add_argument("--description", type=str, required=True, help="The description of the environment")
args = parser.parse_args()

OPENAI_KEY = args.openai_key
DESCRIPTION = args.description

logging.info(f"Description: {DESCRIPTION}")

# Configure OpenAI API key
openai.api_key = OPENAI_KEY

# Set the HOME environment variable for the shell process
shell_env = os.environ.copy()
shell_env['HOME'] = '/userland-scaffold/home/user'

# Command to start the shell in chrooted environment
chroot_command = ['/bin/bash']

# Create a persistent shell process in chrooted environment
shell = subprocess.Popen(
    chroot_command,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=shell_env,
    text=True
)

def execute_command(shell, command):
    logging.info(f"Executing command: {command}")
    
    # Append a unique marker to capture the exit code
    exit_code_marker = '__EXIT_CODE__'
    
    if "cat" in command and "EOF" in command:
        # Handle multi-line commands with 'cat <<EOF'
        shell_command = f'{command}\necho {exit_code_marker}$?' # Add a marker to capture the exit code
    else:
        shell_command = f'{command};echo {exit_code_marker}$?'
    
    # Send the command to the shell
    shell.stdin.write(shell_command + '\n')
    shell.stdin.flush()
    
    exit_code = None
    
    output_lines = []
    error_lines = []
    stdout_fileno = shell.stdout.fileno()
    stderr_fileno = shell.stderr.fileno()
    
    while True:
        # Use select to wait for data on stdout or stderr
        ready_fds, _, _ = select.select([stdout_fileno, stderr_fileno], [], [])
        
        if stdout_fileno in ready_fds:
            line = shell.stdout.readline()
            if not line:
                # EOF
                break
            line = line.rstrip('\n')
            logging.info(line)
            if line.startswith(exit_code_marker):
                # Extract the exit code
                exit_code_str = line[len(exit_code_marker):]
                try:
                    exit_code = int(exit_code_str)
                except ValueError:
                    exit_code = -1
                break
            else:
                output_lines.append(line)
        
        if stderr_fileno in ready_fds:
            err_line = shell.stderr.readline()
            if not err_line:
                # EOF
                break
            err_line = err_line.rstrip('\n')
            error_lines.append(err_line)
            logging.info(err_line)
    
    output = '\n'.join(output_lines)
    error = '\n'.join(error_lines)
    
    logging.info(f"Exit code: {exit_code}")
    return exit_code, output, error

def get_commands_from_gpt(description, messages):
    user_message = f"""
You are an expert in setting up development environments. Your task is to scaffold a new environment using shell commands. Follow these instructions carefully:

1. **Workflow:**
   - Work in sequential steps to set up the environment.
   - For each step:
     - Execute a command.
     - Observe the output.
     - Proceed to the next step based on the results.
2. **Environment Details:**
   - The host system is a Docker container running the base image '{args.base_image}'.
   - You will use your knowledge of this image to determine which tools are available, which are not, and what commands to run.
   - The base path in which you will work is '/home/user'.
3. **Important Notes:**
   - **Check for Existing Tools:**
     - Before installing any tools, check if they are already available and are appropriate for the task.
   - **Non-Interactive Commands Preferred:**
     - Commands should be non-interactive when possible.
     - If a command requires input, be prepared to handle interaction appropriately.
   - **Handling Interactive Commands:**
     - If an interactive command is necessary, include it, and be ready to provide input when prompted.
   - **Handling Failures:**
     - If a step fails, attempt to resolve the issue.
     - Rethink the plan, building off the failed step.
     - Clean up any failed state before continuing, if possible and necessary.
4. **Allowed Actions:**
   - Checking that necessary tools are installed.
   - Installing missing packages and tools using apt-get if necessary.
   - Running tools to set up a project.
   - Creating and writing to files to set up boilerplate code.
   - Changing directories using `cd`.
   - Using `ls` to view directory contents in order to make decisions.
   - Using `cat` to view file contents.
   - Using `sed` to modify files after viewing them with `cat`.
5. **Disallowed Actions:**
   - DO NOT launch long-running processes or development servers.
   - DO NOT use Docker in any way, as Docker is not available or supported in this environment.
6. **Response Guidelines:**
   - **Commands Only:**
     - Respond with a list of shell commands that can be run in sequence.
     - DO NOT provide any additional information, commentary, acknowledgments, or suggestions.
   - **Command Separation:**
     - Separate each set of commands with three hash symbols '###'.
   - **Formatting**:
     - Provide commands as plain text, without any markdown formatting or code blocks.
     - DO NOT include code blocks or triple backticks in your response.
   - **Interactivity:**
     - Ensure commands are non-interactive when possible.
     - If a command requires input, it is acceptable.
   - **Planning:**
     - Stop at any point that requires further thought on how to proceed next.
7. **Examples:**
   - **Writing Files:**
     - Use `mkdir` to create directories before writing files into them.
     - **Example:**
       mkdir -p src
       cat <<EOF > src/file.txt
       This is the content of the file.
       EOF
   - **Sample Task:**
     - **Description:** A simple shell script that outputs the content of `TEST.txt`.
     - **Expected Response:**
       ###
       echo "Hello, World!" > TEST.txt
       ###
       echo -e "echo 'The content of TEST.txt is:'\ncat TEST.txt" > script.sh
"""
    # Add the user's message to the history
    messages.append({"role": "system", "content": user_message})
    
    messages.append({
        "role": "user",
        "content": description
    })
    
    # Get the response from GPT-4
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0
    )
    assistant_message = response.choices[0].message.content.strip()
    
    # Add the assistant's response to the history
    messages.append({"role": "assistant", "content": assistant_message})
    
    # Split the commands
    commands = assistant_message.strip().split('###')
    return commands

# Navigate to /userland-scaffold/home/user
execute_command(shell, 'cd /home/user')
execute_command(shell, 'export DEBIAN_FRONTEND=noninteractive')
execute_command(shell, 'export HOME=/home/user')

# Initialize message history
messages = []

# Get initial commands
logging.info("Getting commands from GPT...")
commands = get_commands_from_gpt(DESCRIPTION, messages)

logging.info("Beginning setup process...")
retry_required = True
while retry_required:
    logging.info(f"Processing {len(commands)} commands...")
    
    for command in commands:
        command = command.strip()
        command_lines = command.split('\n')
        
        # Rebuild `command` without comment lines
        command = '\n'.join([line for line in command_lines if not line.strip().startswith('#')])
        
        if not command.strip():
            continue
        
        logging.info(command)
        exit_code, output, error = execute_command(shell, command)
        
        if exit_code != 0:
            logging.error(f"Command failed with exit code {exit_code}")
            logging.error(f"Error: {error}")
            
            # Prepare the user's error message
            user_error_message = f"""
    The following command failed with exit code {exit_code} and output:

    {output[-1200:]}
    {error[-1200:]}

    Original command:
    {command}

    Fix this issue and provide a revised plan continuing from the failed command. Remember to clean up any failed state before continuing, if necessary.
    """
    
            logging.info(user_error_message)
    
            # Add the error message to the history
            messages.append({"role": "user", "content": user_error_message})
            
            # Get the corrected command from GPT-4
            correction_response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            corrected_command = correction_response.choices[0].message.content.strip()
            commands = corrected_command.split('###')
            
            # Add the assistant's corrected command to the history
            messages.append({"role": "assistant", "content": corrected_command})
            logging.info(f"Corrected command: {corrected_command}")
            
            # Break out and re-process
            logging.info(f"Processing {len(commands)} new commands...")
            retry_required = True
            break            
        else:
            logging.info("Command executed successfully.")
            logging.info(f"Output: {output}")
            
            success_message = f"""
Command executed successfully: {command}
Output:
{output[-500:]}
"""
            
            messages.append({
                "role": "user",
                "content": success_message.strip()
            })
            
            retry_required = False
            
    logging.info("Setup steps have been processed")

#sys.exit(1)

# Close the shell process
shell.stdin.close()
shell.stdout.close()
shell.stderr.close()
shell.wait()

# Set ownership to user
subprocess.run(["chown", "-R", "user:user", "/home/user"], check=True)

# Set permissions to 777
subprocess.run(["chmod", "-R", "777", "/home/user"], check=True)