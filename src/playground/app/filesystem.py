from typing import List, Literal, Optional, Callable, TypedDict
import os
from watchdog.observers import Observer
from watchdog.events import DirCreatedEvent, DirDeletedEvent, DirMovedEvent, FileCreatedEvent, FileDeletedEvent, FileMovedEvent, FileSystemEventHandler

IGNORED_SYSTEM_DOTFILES = {
    '.profile', '.bashrc', '.bash_profile', '.bash_logout', '.gitignore', '.git', '.DS_Store'
}

class FilesystemEntry(TypedDict):
    name: str
    path: str
    type: Literal["file", "directory"]
    children: Optional[List["FilesystemEntry"]]  # Recursive type

def create_filesystem_entry(entry_type: Literal["file", "directory"], path: str) -> bool:
    """
    Command to create a new entry in the filesystem

    Args:
        entry_type (Literal["file", "directory"]): The type of the entry
        path (str): The path of the entry
    """

    # Strip ., / and .. from the path
    path = os.path.normpath(path)
    
    # Define the base path (user's home directory)
    base_path = "/userland/home/user"
    
    # Build the full path
    full_path = os.path.join(base_path, path)
    
    if entry_type == "file":
        # Check if the file already exists
        if os.path.exists(full_path):
            return False
        
        with open(full_path, "w") as f:
            f.write("")
            
        return True
            
    elif entry_type == "directory":
        os.makedirs(full_path, exist_ok=True)
        
        return True
    
    return False

def read_file_content(path: str) -> str:
    """
    Reads the content of a file

    Args:
        path (str): The path of the file

    Returns:
        str: The content of the file
    """

    with open(path, "r") as f:
        return f.read()
    
def save_file_content(path: str, content: str) -> None:
    """
    Saves the content of a file

    Args:
        path (str): The path of the file
        content (str): The content to save
    """

    with open(path, "w") as f:
        f.write(content)

def get_filesystem_entries(directory: str) -> List[FilesystemEntry]:
    entries: List[FilesystemEntry] = []
    
    # Walk through the directory contents
    for entry_name in os.listdir(directory):
        # Skip ignored dot files
        if entry_name in IGNORED_SYSTEM_DOTFILES:
            continue

        full_path = os.path.join(directory, entry_name)
        if os.path.isdir(full_path):
            # If it's a directory, recursively get its children
            entries.append(FilesystemEntry(
                name=entry_name,
                path=full_path,
                type="directory",
                children=get_filesystem_entries(full_path)
            ))
        else:
            # If it's a file, just add the file entry without children
            entries.append(FilesystemEntry(
                name=entry_name,
                path=full_path,
                type="file",
                children=None
            ))

    return entries

class DirectoryMonitor:
    watch_directory: str
    callback: Callable[[], None]
    event_handler: FileSystemEventHandler
    
    def __init__(self, directory: str, callback: Callable[[], None]) -> None:
        self.watch_directory = directory
        self.callback = callback
        self.event_handler = self.ChangeHandler(callback)
        self.observer = Observer() 
        
    def start_watching(self):
        self.observer.schedule(self.event_handler, self.watch_directory, recursive=True)
        self.observer.start()
        
    def stop_watching(self):
        self.observer.stop()
        self.observer.join()
        
    class ChangeHandler(FileSystemEventHandler):
        callback: Callable[[], None]
        
        def __init__(self, callback: Callable[[], None]) -> None:
            self.callback = callback
            
        def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
            self.callback()
            
        def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
            self.callback()
            
        def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None:
            self.callback()