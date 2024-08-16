#!/bin/bash
chroot /userland /bin/bash

# Write to ~/.bashprofile to start the shell in the userland directory
echo "cd /userland" >> ~/.bash_profile

# Run the entrypoint script
source ~/.bash_profile