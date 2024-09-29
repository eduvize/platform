import os
import subprocess
import time
import logging
import uuid
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Global variables to manage threading
polling_thread = None
polling_stop_event = threading.Event()

def is_container_running(container_name):
    """
    Checks if a given container is in the running state.
    """
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format={{.State.Running}}", container_name],
            capture_output=True,
            text=True,
            check=True
        )
        is_running = result.stdout.strip() == "true"
        if is_running:
            logging.info(f"Container {container_name} is running.")
        else:
            logging.info(f"Container {container_name} is not running yet.")
        return is_running
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to check container status: {e}")
        return False

def wait_for_container(container_name, timeout=300, poll_interval=5):
    """
    Waits for the container to be in a running state, with a specified timeout.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_container_running(container_name):
            return True
        logging.info(f"Waiting for container {container_name} to be fully up...")
        time.sleep(poll_interval)
    
    logging.error(f"Timed out waiting for container {container_name} to be running.")
    return False

def image_exists(image_tag):
    """
    Checks if the image with the given tag exists in a remote registry.
    Returns True if the image is found, otherwise False.
    """
    try:
        # Try pulling the image without downloading it.
        logging.info(f"Checking if image {image_tag} exists in remote repository.")
        result = subprocess.run(
            ["docker", "pull", image_tag],
            capture_output=True,
            text=True
        )
        # Check the output to determine if the image exists or failed to pull
        if "Image is up to date" in result.stdout or "Downloaded newer image" in result.stdout:
            logging.info(f"Image {image_tag} exists in remote repository.")
            return True
        else:
            logging.info(f"Image {image_tag} does not exist in remote repository.")
            return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Error checking remote image: {e}")
        return False

def run_container(image_tag, container_name="my_playground_container"):
    """
    Runs a Docker container from the image with the provided tag.
    """
    try:
        logging.info(f"Attempting to run container {container_name} from image {image_tag}.")

        env = {
            "HOSTNAME": os.getenv("HOSTNAME"),
        }
        
        if os.path.exists("/userland"):
            # Remove the existing /userland directory recursively with all its contents using rm -rf
            subprocess.run(["rm", "-rf", "/userland"], check=True)
        
        os.makedirs("/userland", exist_ok=True)

        logging.info(f"Environment variables: {env}")

        # Build a list of --env arguments for each environment variable
        env_args = [f"--env={key}={value}" for key, value in env.items() if value is not None]

        # Run the container with the specified environment variables
        subprocess.run(
            ["docker", "run", "--name", container_name, "--rm", "-d", "-v", "/userland:/home/user", *env_args, image_tag],
            check=True
        )
        
        # Make /userland 777
        subprocess.run(["chmod", "777", "-R", "/userland"], check=True)
        
        # Run docker command to copy /userland files to /home/user, then delete the temporary /userland directory
        subprocess.run(["docker", "exec", container_name, "cp", "-a", "/userland/.", "/home/user"], check=True)
        subprocess.run(["docker", "exec", container_name, "rm", "-rf", "/userland"], check=True)
        
        # Make all files in /home/user owned by user
        subprocess.run(["docker", "exec", container_name, "chown", "-R", "user:user", "/home/user"], check=True)
        
        # Set permissions to 777 for all files in /home/user
        subprocess.run(["docker", "exec", container_name, "chmod", "-R", "777", "/home/user"], check=True)

        logging.info(f"Container {container_name} is now running.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to run container: {e}")

def stop_and_remove_container(container_name):
    """
    Stops and removes a Docker container if it exists.
    """
    try:
        subprocess.run(["docker", "rm", "-f", container_name], check=True)
        logging.info(f"Container {container_name} has been removed.")
    except subprocess.CalledProcessError:
        logging.info(f"No container named {container_name} found to remove.")

def poll_for_image(image_tag, poll_interval=10):
    """
    Polls for a specific image tag continuously until it's available or until canceled.
    """
    while not polling_stop_event.is_set():
        logging.info(f"Polling for image {image_tag}...")
        if image_exists(image_tag):
            logging.info(f"Image {image_tag} is available. Proceeding to run container.")
            return True
        else:
            logging.info(f"Image {image_tag} is not available. Waiting {poll_interval} seconds before retrying.")
            time.sleep(poll_interval)
    logging.info("Polling has been canceled.")
    return False

def poll_and_run_container(image_tag):
    # Poll for the image
    if poll_for_image(image_tag):
        # Run the container once the image is found
        run_container(image_tag, container_name="my_playground_container")
    else:
        logging.info("Image polling was canceled before the image became available.")

def initialize_environment(image_tag: str):
    global polling_thread
    logging.info(f"Starting to poll for Docker image with tag: {image_tag}")

    # Stop any existing polling
    if polling_thread and polling_thread.is_alive():
        logging.info("An existing initialization is in progress. Canceling it.")
        polling_stop_event.set()
        polling_thread.join()
        polling_stop_event.clear()

    # Clean up any existing containers
    stop_and_remove_container("my_playground_container")
    
    # Remove /userland, if it exists
    if os.path.exists("/userland"):
        subprocess.run(["rm", "-rf", "/userland"], check=True)

    # Start polling in a separate thread
    polling_thread = threading.Thread(target=poll_and_run_container, args=(image_tag,))
    polling_thread.start()

    if not wait_for_container("my_playground_container"):
        raise TimeoutError("Timed out waiting for the container to start.")