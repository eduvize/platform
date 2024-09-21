#!/bin/bash

# Sleep 2 seconds
sleep 2

echo "Listing contents of /userland before copying:"
ls -al /userland

echo "Listing contents of /home/user before copying:"
ls -al /home/user

# Copy all content from /userland to /home/user, including hidden files
echo "Copying files from /userland to /home/user..."
cp -av /userland/. /home/user/

echo "Copy operation completed."

echo "Listing contents of /home/user after copying:"
ls -al /home/user

echo "Removing setup directory"
rm -rf /setup

# Keep the container running
tail -f /dev/null
