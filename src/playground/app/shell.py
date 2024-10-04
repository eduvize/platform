import fcntl
import logging
import os
import struct
import termios
import threading
from time import sleep
from typing import Optional
import socketio
import pty
import signal
import select
from .filesystem import DirectoryMonitor, get_top_level_filesystem_entries

logger = logging.getLogger("Shell")

class Shell:
    terminated: bool
    client: Optional[socketio.Client]
    process_pid: int
    master_fd: int
    directory_monitor: DirectoryMonitor

    def __init__(self, client: socketio.Client):
        self.client = client
        self.stop_signal = threading.Event()
        self.terminated = False

    def start(self):
        self.terminated = False
        self.stop_signal = threading.Event()
        
        self.directory_monitor = DirectoryMonitor(
            directory="/userland", 
            callback=lambda dir_path: 
                self.client.emit("directory_contents", {
                    "path": dir_path[len("/userland/"):],
                    "entries": get_top_level_filesystem_entries(dir_path)
                }) if not self.terminated else None
        )
        
        logger.info("Starting directory monitor")
        self.directory_monitor.start_watching()
        
        logger.info("Starting shell process")

        def read(fd):
            while not self.stop_signal.is_set() and not self.terminated:
                sleep(0.01)
                (data_ready, _, _) = select.select([fd], [], [], 0.1)
                
                if data_ready:
                    output = os.read(fd, 1024 * 20).decode(errors="ignore")
                    if output and not self.terminated:
                        self.client.emit('terminal_output', output)

        pid, fd = pty.fork()
        if pid == 0:
            os.execvp('docker', ['docker', 'exec', '-i', '--env', 'TERM=xterm-256color', '--env', 'HOME=/home/user', '--env', 'PS1=user@eduvize:\\w\\$ ', 'my_playground_container', 'su', 'user', '-c', 'bash'])
        else:
            self.process_pid = pid  # Store the child PID for later termination
            self.master_fd = fd
            self.output_thread = threading.Thread(target=read, args=(fd,))
            self.output_thread.start()

    def terminate(self):
        # Stop monitoring the directory
        self.directory_monitor.stop_watching()
        
        self.terminated = True
        self.stop_signal.set()
        if hasattr(self, 'process_pid'):
            logger.info(f"Terminating process with PID {self.process_pid}")
            os.kill(self.process_pid, signal.SIGTERM)  # Kill the child process

        if self.output_thread.is_alive():
            try:
                self.output_thread.join()
            except Exception as e:
                logger.error(f"Error joining output thread: {e}")

    def send_input(self, t_input: str):
        if self.master_fd:
            logger.info(f"Received input from client: {t_input}")
            os.write(self.master_fd, t_input.encode())

    def resize(self, rows: int, columns: int):
        if getattr(self, 'master_fd', None):
            fcntl.ioctl(
                self.master_fd,
                termios.TIOCSWINSZ,
                struct.pack("HHHH", rows, columns, 0, 0)
            )
