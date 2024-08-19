import socketio
import threading
from .config import get_backend_socketio_endpoint, get_max_wait_time
from .shell import Shell
from .orchestration import mark_for_deletion

endpoint = get_backend_socketio_endpoint()
client = socketio.Client()
shell = Shell(client)
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
def user_connected():
    print("User connected")
    
    cancel_user_connection_timer()
    
@client.event
def user_disconnected():
    print("User disconnected")
    
    mark_for_deletion()

def connect_to_server(token: str):
    client.connect(
        url=endpoint,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    client.wait()
    
start_user_connection_timer()