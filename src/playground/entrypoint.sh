#!/bin/bash

# Check if /playground/userland-scaffold exists, if not, create it
if [ ! -d /playground/userland-scaffold ]; then
    echo "Creating /userland-scaffold..."
    cp -a /userland-scaffold/. /playground/userland-scaffold/
fi

# Copy the entrypoint.sh script to the shared volume
echo "Copying entrypoint.sh to shared playground volume..."

cp -f /entrypoint.sh /playground/entrypoint.sh
chmod +x /playground/entrypoint.sh

# If /userland exists, remove it
if [ -d /userland ]; then
    # Kill any processes belonging to 'user'
    chroot /userland pkill -9 -u user 2>/dev/null || true

    echo "Removing existing /userland files..."
    rm -rf /userland/*
fi

# Copy the debootstrap environment into the shared volume
echo "Copying debootstrap environment to /userland..."
sync
cp -a /playground/userland-scaffold/. /userland/
cp -a /usr/share/terminfo /userland/usr/share/

# Create /dev/null and other device nodes
mknod -m 666 /userland/dev/null c 1 3
mknod -m 666 /userland/dev/zero c 1 5
mknod -m 666 /userland/dev/random c 1 8
mknod -m 666 /userland/dev/urandom c 1 9

# Create the sandbox user
chroot /userland groupadd -g 1000 user
chroot /userland useradd -m -s /bin/bash -d /home/user -u 1000 -g 1000 user

# Rewrite PS1 to show the user that they are in a sandbox (user@sandbox $)
chroot /userland bash -c "echo 'PS1=\"\[\033[01;32m\]\u@\[\033[01;34m\]sandbox:\w\[\033[00m\] \$ \"' >> /home/user/.bashrc"

# Force the user into their home directory upon login
chroot /userland bash -c "echo 'cd /home/user' >> /home/user/.bashrc"

# Set ownership and permissions
chroot /userland chown -R root:root /
chroot /userland chown -R user:user /home/user  # Allow user to write in their home directory
chroot /userland chmod -R 0777 /home/user  # Ensure the user can write
chroot /userland chmod -R 0755 /

# Install python3, pip3, and nano packages
chroot /userland apt-get update -y && chroot /userland apt-get install -y python3 nano

echo "This is a sandbox environment for your Eduvize course.
You can use this environment to run commands and programs
without affecting your host system, and your tutor will
be able to see what you are doing and assist you.
" > /userland/NOTICE.txt