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
    ARG OPENAI
    ARG SCAFFOLD_DESCRIPTION

    COPY install_dependencies.sh .
    RUN chmod +x ./install_dependencies.sh
    RUN ./install_dependencies.sh
    
    ENV PATH="/env/bin:$PATH"

    RUN useradd -m -s /bin/bash -d /home/user user

    # Copy the installer executable
    COPY --from=packager /setup/dist/installer /usr/local/bin/installer
    
    # Run the installer
    RUN installer --openai_key $OPENAI --description "$SCAFFOLD_DESCRIPTION"

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