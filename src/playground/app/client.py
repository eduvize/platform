import logging
import time
from typing import Literal, Optional
import uuid
import socketio
import threading
from .config import get_backend_socketio_endpoint, get_self_destruct_enabled, get_image_tag
from .shell import Shell
from .orchestration import mark_for_deletion
from .filesystem import create_filesystem_entry, read_file_content, save_file_content, rename_path, delete_path, get_top_level_filesystem_entries
from .container_runtime import initialize_environment
from .monitoring import run_exercise_monitor, stop_exercise_monitor, handle_filesystem_change

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = socketio.Client()
shell = None
user_connection_timer = None
is_user_connected = False
environment_type: Optional[Literal["exercise"]] = None
exercise_id: Optional[uuid.UUID] = None

def self_destruct():
    global is_user_connected
    
    if is_user_connected:
        logger.info("User is connected. Skipping self-destruct.")
        return
    
    logger.info("Self-destructing...")
    mark_for_deletion()

def start_user_connection_timer():
    global user_connection_timer
    
    if user_connection_timer is not None:
        logging.info("Cancelling existing user connection timer")
        user_connection_timer.cancel()
        user_connection_timer = None        
    
    user_connection_timer = threading.Timer(10.0, self_destruct)
    user_connection_timer.start()
    logging.info("User connection timer started")

def cancel_user_connection_timer():
    global user_connection_timer
    if user_connection_timer is not None:
        logging.info("Cancelling user connection timer")
        user_connection_timer.cancel()
        user_connection_timer = None

@client.event
def connect():
    logging.info("Connected to server")
    
    if get_self_destruct_enabled():
        start_user_connection_timer()
            
@client.event
def disconnect():
    logging.info("Disconnected from server")
    
    if get_self_destruct_enabled():
        mark_for_deletion()
        
@client.event
def start_exercise_monitoring(data: dict):
    global environment_type, client, exercise_id
    environment_type = "exercise"
    exercise_id = uuid.UUID(data.get("exercise_id"))
      
@client.event
def subscribe_to_path(data: dict):
    """
    Subscribes to a filesystem path for changes

    Args:
        data (dict): The filesystem entry data
    """
    
    path = data.get("path").lstrip("/")
    shell.directory_monitor.add_path(path)
    
@client.event
def unsubscribe_from_path(data: dict):
    """
    Unsubscribes from a filesystem path

    Args:
        data (dict): The filesystem entry data
    """
    
    path = data.get("path").lstrip("/")
    shell.directory_monitor.remove_path(path)
        
@client.event
def get_directory(data: dict):
    """
    Command to get the directory tree

    Args:
        data (dict): The filesystem entry data
    """
    
    path = data.get("path").lstrip("/")
    
    client.emit("directory_contents", {
        "path": path,
        "entries": get_top_level_filesystem_entries(path)
    })
        
@client.event
def terminal_input(t_input: str):
    """
    Proxies an event from the user to the playground controller shell

    Args:
        command (str): The command to execute
    """
    shell.send_input(t_input)

@client.event
def terminal_resize(data: dict):
    """
    Proxies an event from the user to the playground controller shell

    Args:
        data (dict): The terminal size data
    """
    
    rows = data.get("rows", 24)
    columns = data.get("columns", 80)
    
    shell.resize(
        rows=rows,
        columns=columns
    )
    
@client.event
def create(data: dict):
    """
    Command to create a new entry in the filesystem

    Args:
        data (dict): The filesystem entry data
    """
    
    entry_type = data.get("type")
    path = data.get("path")
    
    success = create_filesystem_entry(
        entry_type=entry_type,
        path=path
    )
    
    if not success:
        pass #TODO: Send an alert to the user
    
@client.event
def rename(data: dict):
    """
    Command to rename an entry in the filesystem

    Args:
        data (dict): The filesystem entry data
    """
    
    old_path = data.get("path")
    new_path = data.get("new_path")
    
    rename_path(old_path, new_path)
    
@client.event
def delete(data: dict):
    """
    Command to delete an entry in the filesystem

    Args:
        data (dict): The filesystem entry data
    """
    
    path = data.get("path")
    
    delete_path(path)
    
@client.event
def open_file(data: dict):
    """
    Command to open a file in the filesystem

    Args:
        data (dict): The filesystem entry data
    """
    
    path = data.get("path").lstrip("/")
    content = read_file_content(path)
    
    client.emit("file_content", {
        "path": path,
        "content": content or ""
    })
    
@client.event
def save_file(data: dict):
    """
    Command to save a file in the filesystem

    Args:
        data (dict): The filesystem entry data
    """
    
    path = data.get("path")
    content = data.get("content")

    save_file_content(path, content)
    handle_filesystem_change(path)

@client.event
def user_connected(data: dict):
    logger.info("User connected")
    
    global is_user_connected, environment_type, exercise_id
    is_user_connected = True
    
    cancel_user_connection_timer()
    
    image_tag = get_image_tag()
    if image_tag is None:
        image_tag = data.get("image_tag", None)
        
        if image_tag is None:
            logger.error("No image tag provided")
            return

    logger.info(f"Initializing environment with image tag: {image_tag}")
    initialize_environment(image_tag)
            
    shell.start()
    
    if environment_type == "exercise":
        logger.info(f"Starting exercise monitoring for exercise: {exercise_id}")
        run_exercise_monitor(client, exercise_id)
    
    client.emit("ready")
    
@client.event
def user_disconnected():
    logger.info("User disconnected")
    
    global is_user_connected
    is_user_connected = False
    
    if environment_type == "exercise":
        stop_exercise_monitor()
    
    if get_self_destruct_enabled():
        mark_for_deletion()
    else:
        shell.terminate()
    
def connect_to_server(token: str, max_retries: int = 3, retry_delay: int = 5):
    """
    Attempts to connect to the server, retrying on failure up to `max_retries` times with a delay of `retry_delay` seconds.
    
    Args:
        token (str): The authorization token to connect to the server.
        max_retries (int): The maximum number of retries before giving up. Defaults to 3.
        retry_delay (int): The delay in seconds between retries. Defaults to 5.
    """
    
    global client, shell
    
    endpoint = get_backend_socketio_endpoint()
    shell = Shell(client)
    
    attempt = 0
    while attempt < max_retries:
        try:
            logging.info(f"Attempt {attempt + 1} to connect to the server.")
            client.connect(
                url=endpoint,
                headers={
                    "Authorization": f"Bearer {token}"
                },
                retry=True,
            )
            logging.info("Connection successful!")
                
            client.wait()  # Blocks the main thread, ensuring client remains connected
            
            break  # Exit the loop if connection is successful

        except Exception as e:
            attempt += 1
            logging.warning(f"Connection attempt {attempt} failed: {e}")
            
            if attempt < max_retries:
                logging.warning(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error("Max retries reached. Could not connect to the server.")