import logging
import time
import socketio
import threading
from .config import get_backend_socketio_endpoint, get_self_destruct_enabled
from .shell import Shell
from .orchestration import mark_for_deletion
from .filesystem import create_filesystem_entry, read_file_content, save_file_content, rename_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = socketio.Client()
shell = None
user_connection_timer = None

def start_user_connection_timer():
    global user_connection_timer
    if user_connection_timer is None:
        user_connection_timer = threading.Timer(10.0, mark_for_deletion)
        user_connection_timer.start()
        print("User connection timer started")
    else:
        print("User connection timer is already running")

def cancel_user_connection_timer():
    global user_connection_timer
    if user_connection_timer is not None:
        print("Cancelling user connection timer")
        user_connection_timer.cancel()
        user_connection_timer = None
    else:
        print("No active timer to cancel")

@client.event
def connect():
    print("Connected to server")
    
    shell.start()
        
@client.event
def disconnect():
    print("Disconnected from server")
    
    if get_self_destruct_enabled():
        mark_for_deletion()
        
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
def open_file(data: dict):
    """
    Command to open a file in the filesystem

    Args:
        data (dict): The filesystem entry data
    """
    
    path = data.get("path")
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

@client.event
def user_connected():
    logger.info("User connected")
    
    cancel_user_connection_timer()
    
@client.event
def user_disconnected():
    logger.info("User disconnected")
    
    if get_self_destruct_enabled():
        mark_for_deletion()
        
    shell.terminate()
    client.shutdown()
    
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
            print(f"Attempt {attempt + 1} to connect to the server.")
            client.connect(
                url=endpoint,
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )
            print("Connection successful!")
            
            if get_self_destruct_enabled():
                start_user_connection_timer()
                
            client.wait()  # Blocks the main thread, ensuring client remains connected
            
            break  # Exit the loop if connection is successful

        except Exception as e:
            attempt += 1
            print(f"Connection attempt {attempt} failed: {e}")
            
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Could not connect to the server.")