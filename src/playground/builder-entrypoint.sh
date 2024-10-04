#!/bin/sh

echo "Starting Docker daemon..."

# Check if /var/run/docker.pid exists
if [ -f /var/run/docker.pid ]; then
    echo "Removing stale Docker PID file..."
    rm /var/run/docker.pid
fi

dockerd &
until docker info >/dev/null 2>&1; do
    echo "Waiting for dockerd to start..."
    sleep 1
done
echo "Docker daemon started."

echo "Logging into Docker registry"
echo "$REGISTRY_CRED" | docker login $REGISTRY -u "$REGISTRY_USER" --password-stdin

unset REGISTRY
unset REGISTRY_USER
unset REGISTRY_CRED

echo "Running setup listener..."
cd /
python -m setup.listener