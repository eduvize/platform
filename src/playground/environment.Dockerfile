# Use Ubuntu 20.04 LTS as base image
FROM ubuntu:20.04

# Avoid any prompts during package installations
ARG DEBIAN_FRONTEND=noninteractive

# Update packages and install necessary utilities
RUN apt-get update && apt-get install -y \
    debootstrap

# Create the necessary directories
RUN mkdir /playground-hidden && \
    mkdir /userland && \
    mkdir -p /userland/home/user

RUN touch /userland/youarehere.txt

# Set up a basic bashrc in the playground-hidden directory
RUN echo 'export PS1="\\u:\\w\\$ "' > /playground-hidden/bashrc

# Use debootstrap to create a minimal chroot environment
RUN debootstrap --variant=minbase bookworm /userland

RUN rm -rf /var/lib/apt/lists/*

# Create an unprivileged user
RUN useradd -m -s /userland/bin/bash -d /userland/home/user user

# Create a .bashrc in the user's home directory, cd into /userland
RUN echo 'export PS1="\\u@userland:\\w\\$ "' > /userland/home/user/.bashrc

# Set ownership and permissions
RUN chown -R root:root /userland && \
    chmod -R 0755 /userland

COPY entrypoint.sh /entrypoint.sh


# Set the entrypoint to use chroot
ENTRYPOINT ["/entrypoint.sh"]