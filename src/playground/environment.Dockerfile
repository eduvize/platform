# Use Ubuntu 20.04 LTS as base image
FROM ubuntu:20.04

# Avoid any prompts during package installations
ARG DEBIAN_FRONTEND=noninteractive

# Update packages and install necessary utilities
RUN apt-get update && apt-get install -y \
    debootstrap \
    rsync

# Set up a debootstrap environment
RUN debootstrap --variant=minbase --include=bash,netbase focal /userland-scaffold

# Install nano into the debootstrap environment
RUN chroot /userland-scaffold apt-get update && chroot /userland-scaffold apt-get install -y nano

# Make bash executable in the debootstrap environment
RUN chmod +x /userland-scaffold/bin/bash

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use CMD to run the entrypoint script and then sleep indefinitely
CMD ["/bin/bash", "-c", "/entrypoint.sh && sleep infinity"]