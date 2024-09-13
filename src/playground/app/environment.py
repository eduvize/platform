from typing import List, TypedDict
from .filesystem import FilesystemEntry, get_filesystem_entries

class EnvironmentSnapshot(TypedDict):
    filesystem: List[FilesystemEntry]

def get_environment_snapshot():
    return EnvironmentSnapshot(
        filesystem=get_filesystem_entries("/userland/home/user")
    )