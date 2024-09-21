#!/bin/sh

echo "Starting Docker daemon..."
dockerd &
until docker info >/dev/null 2>&1; do
    echo "Waiting for dockerd to start..."
    sleep 1
done
echo "Docker daemon started."

echo "Logging into Docker registry"
echo "$REGISTRY_CRED" | docker login $REGISTRY -u "$REGISTRY_USER" --password-stdin

unset REGISTRY_CRED
unset REGISTRY_USER
unset REGISTRY

echo "Running controller.run..."
cd /
python -m controller.run
