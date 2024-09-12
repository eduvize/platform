import fcntl
import logging
import os
import struct
import termios
import threading
from typing import Optional
import socketio
import pty
import pwd
import signal
from .filesystem import DirectoryMonitor
from .environment import get_environment_snapshot

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
        self.directory_monitor = DirectoryMonitor(
            directory="/userland/home/user", 
            callback=lambda: 
                self.client.emit("environment", get_environment_snapshot())
        )

    def start(self):
        logger.info("Starting directory monitor")
        self.directory_monitor.start_watching()
        
        logger.info("Starting shell process")

        def read(fd):
            while not self.stop_signal.is_set():
                output = os.read(fd, 1024)  # Read from PTY master
                if output and not self.terminated:
                    self.client.emit('terminal_output', output.decode('utf-8', errors='replace'))

        pid, fd = pty.fork()
        if pid == 0:  # Child process
            os.chroot("/userland")
            os.chdir("/")  # Change to the root directory inside chroot
            os.environ['TERM'] = 'xterm-256color'
            os.environ['HOME'] = '/home/user'
            # Drop privileges to "user"
            user_info = pwd.getpwnam("user")
            os.setgid(user_info.pw_gid)  # Set group ID
            os.setuid(user_info.pw_uid)  # Set user ID

            os.execv('/bin/bash', ['/bin/bash', '-i'])
        else:  # Parent process
            self.process_pid = pid  # Store the child PID for later termination
            self.master_fd = fd
            self.output_thread = threading.Thread(target=read, args=(fd,))
            self.output_thread.start()
            
            # Send the first state of the environment
            self.client.emit("environment", get_environment_snapshot())

    def terminate(self):
        # Stop monitoring the directory
        self.directory_monitor.stop_watching()
        
        self.terminated = True
        self.stop_signal.set()
        if hasattr(self, 'process_pid'):
            logger.info(f"Terminating process with PID {self.process_pid}")
            os.kill(self.process_pid, signal.SIGTERM)  # Kill the child process

        if self.output_thread.is_alive():
            self.output_thread.join()

    def send_input(self, t_input: str):
        if self.master_fd:
            logger.info(f"Received input from client: {t_input}")
            os.write(self.master_fd, t_input.encode('utf-8'))  # Write to PTY

    def resize(self, rows: int, columns: int):
        if self.master_fd:
            fcntl.ioctl(
                self.master_fd,
                termios.TIOCSWINSZ,
                struct.pack("HHHH", rows, columns, 0, 0)
            )

    def _gather_output(self):
        logger.info("Beginning to stream output")

        while not self.stop_signal.is_set():
            output = self.master_fd.read(1)  # Read one byte at a time
            if output and not self.terminated:
                self.client.emit('terminal_output', output.decode('utf-8', errors='replace'))

    def _emit_output(self, line: bytes):
        if not self.terminated:
            self.client.emit('terminal_output', line.decode('utf-8', errors='replace'))
