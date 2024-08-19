import fcntl
import logging
import os
import struct
import subprocess
import termios
import threading
import socketio
import pty
import pwd

logger = logging.getLogger("Shell")

class Shell:
    client: socketio.Client
    process: subprocess.Popen

    def __init__(self, client: socketio.Client):
        self.client = client
        self.stop_signal = threading.Event()

    def start(self):
        logger.info("Starting shell process")

        def read(fd):
            while not self.stop_signal.is_set():
                output = os.read(fd, 1024)  # Read from PTY master
                if output:
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
            self.process = fd
            self.master_fd = fd
            self.output_thread = threading.Thread(target=read, args=(fd,))
            self.output_thread.start()

    def terminate(self):
        self.stop_signal.set()
        if self.process:
            self.process.terminate()
            self.process.wait()
        if self.output_thread.is_alive():
            self.output_thread.join()

    def send_input(self, t_input: str):
        if self.process:
            logger.info(f"Received input from client: {t_input}")
            os.write(self.process, t_input.encode('utf-8'))  # Write to PTY
            # Echo input back to xterm.js immediately
            #self.client.emit('terminal_output', t_input)
            
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
            output = self.process.stdout.read(1)  # Read one byte at a time
            if output:
                self.client.emit('terminal_output', output.decode('utf-8', errors='replace'))

    def _emit_output(self, line: bytes):
        self.client.emit('terminal_output', line.decode('utf-8', errors='replace'))
