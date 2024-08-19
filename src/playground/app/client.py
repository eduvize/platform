import socketio
from .config import get_backend_socketio_endpoint
from .shell import Shell
from .orchestration import mark_for_deletion

endpoint = get_backend_socketio_endpoint()
client = socketio.Client()
shell = Shell(client)

@client.event
def connect():
    print("Connected to server")
    
    shell.start()
        
@client.event
def disconnect():
    print("Disconnected from server")
        
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