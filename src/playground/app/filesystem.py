import shutil
from typing import List, Literal, Optional, Callable, TypedDict
import os
from watchdog.observers import Observer
from watchdog.events import DirCreatedEvent, DirDeletedEvent, DirModifiedEvent, DirMovedEvent, FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent, FileSystemEventHandler

IGNORED_SYSTEM_DOTFILES = {
    '.profile', '.bashrc', '.bash_profile', '.bash_logout', '.gitignore', '.git', '.DS_Store'
}

class FilesystemEntry(TypedDict):
    name: str
    path: str
    type: Literal["file", "directory"]

def create_filesystem_entry(entry_type: Literal["file", "directory"], path: str) -> bool:
    """
    Command to create a new entry in the filesystem

    Args:
        entry_type (Literal["file", "directory"]): The type of the entry
        path (str): The path of the entry
    """

    # Remove leading /'s from the path
    path = path.lstrip("/")
    
    # Define the base path (user's home directory)
    base_path = "/userland"
    
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

    # Trim leading /'s from the path
    path = path.lstrip("/")

    base_path = "/userland"

    full_path = os.path.join(base_path, path)

    with open(full_path, "r") as f:
        return f.read()
    
def rename_path(old_path: str, new_path: str) -> None:
    """
    Renames a file or directory

    Args:
        old_path (str): The old path
        new_path (str): The new path
    """

    # Trim leading /'s from the path
    old_path = old_path.lstrip("/")
    new_path = new_path.lstrip("/")

    base_path = "/userland"

    old_full_path = os.path.join(base_path, old_path)
    new_full_path = os.path.join(base_path, new_path)

    os.rename(old_full_path, new_full_path)
    
def delete_path(path: str) -> None:
    """
    Deletes a file or directory recursively if it's a directory.

    Args:
        path (str): The path to delete
    """
    # Trim leading /'s from the path
    path = path.lstrip("/")

    base_path = "/userland"
    full_path = os.path.join(base_path, path)

    if os.path.isdir(full_path):
        shutil.rmtree(full_path)  # Recursively delete directory and its contents
    else:
        os.remove(full_path)  # Delete a file
    
def save_file_content(path: str, content: str) -> None:
    """
    Saves the content of a file

    Args:
        path (str): The path of the file
        content (str): The content to save
    """

    # Trim leading /'s from the path
    path = path.lstrip("/")
    
    base_path = "/userland"
    
    full_path = os.path.join(base_path, path)

    with open(full_path, "w") as f:
        f.write(content)

def get_top_level_filesystem_entries(directory: str) -> List[FilesystemEntry]:
    entries: List[FilesystemEntry] = []
    base_path = "/userland"
    full_dir_path = os.path.join(base_path, directory)
    
    # Walk through the top-level directory contents
    for entry_name in os.listdir(full_dir_path):
        # Skip ignored dot files
        if entry_name in IGNORED_SYSTEM_DOTFILES:
            continue
        
        full_path = os.path.join(base_path, directory, entry_name)
        
        # Trim the directory path from the full path
        rel_path = os.path.relpath(full_path, base_path)
        
        # Trim leading /'s from the path
        rel_path = rel_path.lstrip("/")

        # Only collect top-level directory/file info without recursion
        if os.path.isdir(full_path):
            entries.append(FilesystemEntry(
                name=entry_name,
                path=rel_path,
                type="directory",
            ))
        else:
            entries.append(FilesystemEntry(
                name=entry_name,
                path=rel_path,
                type="file",
            ))

    return entries

class DirectoryMonitor:
    watch_directory: str
    callback: Callable[[], None]
    event_handler: FileSystemEventHandler
    subscribed_paths: List[str]
    trigger_on_modified: bool
    no_path_filter: bool
    
    def __init__(
        self, 
        directory: str, 
        callback: Callable[[str], None], 
        trigger_on_modified: bool = False, 
        no_path_filter: bool = False
    ) -> None:
        self.watch_directory = directory
        self.callback = callback
        self.event_handler = self.ChangeHandler(self, callback)
        self.observer = Observer()
        self.subscribed_paths = [directory] 
        self.trigger_on_modified = trigger_on_modified
        self.no_path_filter = no_path_filter
        
    def start_watching(self):
        self.observer.schedule(self.event_handler, self.watch_directory, recursive=True)
        self.observer.start()
        
    def stop_watching(self):
        self.observer.stop()
        self.observer.join()
        
    def add_path(self, path: str):
        full_path = os.path.join(self.watch_directory, path)
        
        if full_path not in self.subscribed_paths:
            self.subscribed_paths.append(full_path)
            
    def remove_path(self, path: str):
        full_path = os.path.join(self.watch_directory, path)
        
        if full_path in self.subscribed_paths:
            self.subscribed_paths.remove(full_path)
            
    def is_tracked_path(self, path: str) -> bool:
        return path in self.subscribed_paths
        
    class ChangeHandler(FileSystemEventHandler):
        monitor: "DirectoryMonitor"
        callback: Callable[[str], None]
        
        def __init__(self, monitor: "DirectoryMonitor", callback: Callable[[str], None]) -> None:
            self.monitor = monitor
            self.callback = callback
            
        def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
            dir_path = os.path.dirname(event.src_path)

            if not self.monitor.is_tracked_path(dir_path) and not self.monitor.no_path_filter:
                return
            
            self.callback(dir_path)
            
        def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
            dir_path = os.path.dirname(event.src_path)
            
            if not self.monitor.is_tracked_path(dir_path) and not self.monitor.no_path_filter:
                return
            
            self.callback(dir_path)
            
        def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None:
            src_dir_path = os.path.dirname(event.src_path)
            
            if self.monitor.is_tracked_path(src_dir_path) and not self.monitor.no_path_filter:
                self.callback(src_dir_path)

            dest_dir_path = os.path.dirname(event.dest_path)
            
            if self.monitor.is_tracked_path(dest_dir_path) and not self.monitor.no_path_filter:
                self.callback(dest_dir_path)
                
        def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
            dir_path = os.path.dirname(event.src_path)
            
            if not self.monitor.is_tracked_path(dir_path) and not self.monitor.no_path_filter:
                return
            
            if self.monitor.trigger_on_modified:
                self.callback(dir_path)