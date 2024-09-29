import logging
import os
import subprocess
import sys
from typing import Optional
import uuid

# Set up logging configuration to log at INFO level to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s: %(message)s')

def build_image(openai_key: str, base_image: str, description: str) -> Optional[str]:
    logging.info(f"""
    Base image: {base_image}
    Description: {description}
    """)

    # Dockerfile content based on user input
    dockerfile_content = f"""
    FROM python:3.11-slim AS packager
    RUN apt-get update && apt-get install -y build-essential
    
    # Install pyinstaller
    RUN pip install pyinstaller
    
    WORKDIR /setup
    COPY . .
    
    # Install dependencies
    RUN pip install -r requirements.txt
    
    # Create the executable
    RUN pyinstaller --onefile installer.py
    
    FROM {base_image}
    WORKDIR /app
    ARG OPENAI
    ARG SCAFFOLD_DESCRIPTION

    COPY install_dependencies.sh ./install_dependencies.sh
    RUN chmod +x ./install_dependencies.sh
    RUN ./install_dependencies.sh
    
    # Delete user with UID 1000 if it exists
    RUN uid_to_delete=1000 \\
        && username_to_delete=$(getent passwd | awk -F: -v uid=$uid_to_delete '$3==uid {{print $1}}') \\
        && if [ -n "$username_to_delete" ]; then \\
            userdel -r $username_to_delete; \\
        fi

    # Delete group with GID 1000 if it exists
    RUN gid_to_delete=1000 \\
        && groupname_to_delete=$(getent group | awk -F: -v gid=$gid_to_delete '$3==gid {{print $1}}') \\
        && if [ -n "$groupname_to_delete" ]; then \\
            groupdel -f $groupname_to_delete; \\
        fi
    
    # Create a new group and user with UID and GID 1000
    RUN groupadd -g 1000 user \\
        && useradd -m -s /bin/bash -d /home/user -u 1000 -g 1000 user

    # Copy the installer executable
    COPY --from=packager /setup/dist/installer /usr/local/bin/installer
    
    # Run the installer
    RUN installer --base_image "{base_image}" --openai_key $OPENAI --description "$SCAFFOLD_DESCRIPTION"

    RUN mkdir /userland
    RUN cp -a /home/user/. /userland/ # Copy the user's home directory to /userland

    WORKDIR /home/user
    
    CMD sleep infinity
    """

    image_tag = f"registry.crosswinds.cloud/eduvize/playground:{uuid.uuid4().hex}".replace("-", "")

    # Write Dockerfile
    script_dir = os.path.dirname(os.path.realpath(__file__))
    dockerfile_path = os.path.join(script_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)

    # Build the Docker image
    docker_process = subprocess.Popen(
        ["docker", "build", "-t", image_tag, script_dir, "--build-arg", f"OPENAI={openai_key}", "--build-arg", f"SCAFFOLD_DESCRIPTION={description}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True  # To capture the output as text (not bytes)
    )

    # Log the Docker output
    for line in docker_process.stdout:
        logging.info(line.strip())

    # Wait for the Docker build process to finish
    docker_process.wait()


    # Clean up by removing the Dockerfile after the build
    os.remove(dockerfile_path)

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
        
        return image_tag
    else:
        logging.error(f"Docker build failed with return code {docker_process.returncode}")
        
        return None