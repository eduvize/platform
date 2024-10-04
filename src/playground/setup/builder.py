import uuid
import logging
import os
import subprocess
import sys
from typing import Optional, List
from .models import ExercisePlan, ExerciseFile
import tempfile

class BuildException(Exception):
    """
    Custom exception to be raised when Docker build or push fails.
    """
    def __init__(self, message: str):
        super().__init__(message)

# Set up logging configuration to log at INFO level to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s: %(message)s')

def build_exercise_image(exercise: ExercisePlan) -> Optional[str]:
    # Create a temporary directory to work in
    with tempfile.TemporaryDirectory() as temp_dir:
        dockerfile_content = f"""
FROM {exercise.docker_image}
WORKDIR /app

# Delete user with UID 1000 if it exists
RUN if [ -f /etc/alpine-release ]; then \\
        deluser --remove-home user || true; \\
    elif [ -f /etc/debian_version ]; then \\
        userdel -r user || true; \\
    fi

# Delete group with GID 1000 if it exists
RUN if [ -f /etc/alpine-release ]; then \\
        delgroup user || true; \\
    elif [ -f /etc/debian_version ]; then \\
        groupdel -f user || true; \\
    fi

# Create a new group and user with UID and GID 1000
RUN if [ -f /etc/alpine-release ]; then \\
        addgroup -g 1000 user && adduser -D -u 1000 -G user user; \\
    elif [ -f /etc/debian_version ]; then \\
        groupadd -g 1000 user && useradd -m -s /bin/bash -d /home/user -u 1000 -g user user; \\
    else \\
        echo "Unsupported OS"; exit 1; \\
    fi

# Install basic packages
RUN if [ -f /etc/alpine-release ]; then \\
        apk update && apk add --no-cache git curl wget unzip; \\
    elif [ -f /etc/debian_version ]; then \\
        apt-get update && apt-get install -y git curl wget unzip && rm -rf /var/lib/apt/lists/*; \\
    else \\
        echo "Unsupported OS"; exit 1; \\
    fi

WORKDIR /home/user
"""

        # Install the required packages
        if exercise.system_packages:
            dockerfile_content += create_package_install_commands(exercise.system_packages)
        else:
            dockerfile_content += """
RUN if [ -f /etc/alpine-release ]; then \\
        apk update; \\
    elif [ -f /etc/debian_version ]; then \\
        apt-get update && rm -rf /var/lib/apt/lists/*; \\
    fi
"""

        # Run the prerequisite commands
        if exercise.pre_commands:
            dockerfile_content += create_setup_commands(exercise.pre_commands)

        # Add files to the Dockerfile
        for f in exercise.files:
            dockerfile_content += create_file_copies(f, temp_dir)

        # Run the post-scaffold commands
        if exercise.post_commands:
            dockerfile_content += create_setup_commands(exercise.post_commands)

        # Common operations that don't depend on OS type
        dockerfile_content += """
RUN mkdir /userland
RUN cp -a /home/user/. /userland/ # Copy the user's home directory to /userland

CMD sleep infinity
"""

        logging.info("Generated Dockerfile content:")
        logging.info(dockerfile_content)

        image_tag = f"registry.crosswinds.cloud/eduvize/playground:{uuid.uuid4().hex}"

        # Write Dockerfile
        dockerfile_path = os.path.join(temp_dir, "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)

        docker_logs: List[str] = []

        # Build the Docker image
        try:
            docker_build_command = ["docker", "build", "-t", image_tag, temp_dir]
            docker_process = subprocess.Popen(
                docker_build_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # To capture the output as text (not bytes)
            )

            try:
                # Set a timeout of 120 seconds (2 minutes) for the build process
                stdout, stderr = docker_process.communicate(timeout=120)
            except subprocess.TimeoutExpired:
                docker_process.kill()
                stdout, stderr = docker_process.communicate()
                logging.error("Docker build process timed out after 2 minutes.")
                raise BuildException(f"Docker build timed out. Dockerfile content:\n{dockerfile_content}")

            if stderr:
                logging.error(stderr.strip())
                docker_logs.append(stderr.strip())

            if stdout:
                logging.info(stdout.strip())
                docker_logs.append(stdout.strip())

            # Check if the process completed successfully
            if docker_process.returncode == 0:
                logging.info("Docker image built successfully!")

                # Push the image to the registry
                docker_push_process = subprocess.Popen(
                    ["docker", "push", image_tag],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                # Log the Docker push output
                for line in docker_push_process.stdout:
                    logging.info(line.strip())

                # Wait for the Docker push process to finish
                docker_push_process.wait()

                if docker_push_process.returncode == 0:
                    logging.info("Docker image pushed successfully!")
                    return image_tag
                else:
                    logging.error(f"Docker push failed with return code {docker_push_process.returncode}")
                    return None
            else:
                logging.error(f"Docker build failed with return code {docker_process.returncode}")
                raise BuildException("\n".join(docker_logs) + f"\nDockerfile content:\n{dockerfile_content}")
        except BuildException:
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}\nDockerfile content:\n{dockerfile_content}")
            raise BuildException("\n".join(docker_logs))

def create_package_install_commands(packages: List[str]) -> str:
    """
    Creates a command to install the given packages using the appropriate package manager.
    """
    packages_str = " ".join(packages)
    return f"""
RUN if [ -f /etc/alpine-release ]; then \\
        apk add --no-cache {packages_str}; \\
    elif [ -f /etc/debian_version ]; then \\
        apt-get install -y {packages_str} && rm -rf /var/lib/apt/lists/*; \\
    fi
"""

def create_setup_commands(commands: List[str]) -> str:
    """
    Creates a command to run the given setup commands.
    """
    # Join commands with '&&' to ensure they run sequentially
    command_str = ' && '.join(commands)
    return f"""
RUN if [ -f /etc/alpine-release ]; then \\
        {command_str}; \\
    elif [ -f /etc/debian_version ]; then \\
        {command_str}; \\
    fi
"""

def create_file_copies(file: ExerciseFile, temp_dir: str) -> str:
    """
    Write the file content to a temporary file in temp_dir, to be copied into the Docker image.
    """
    temp_filename = f"temp_{uuid.uuid4().hex}"
    local_file_path = os.path.join(temp_dir, temp_filename)

    with open(local_file_path, "w") as f:
        f.write(file.content)

    dest_dir_path = os.path.dirname(file.path)

    dockerfile_instructions = ""

    if dest_dir_path:
        dockerfile_instructions += f"""
RUN mkdir -p {dest_dir_path}
"""

    dockerfile_instructions += f"""
COPY {temp_filename} {file.path}
"""

    return dockerfile_instructions
