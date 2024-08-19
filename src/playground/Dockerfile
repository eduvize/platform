# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install curl, ca-certificates, apt-transport-https, gnupg2, and lsb-release
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    apt-transport-https \
    gnupg2 \
    lsb-release

# Add the Kubernetes apt repository
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Command to run the application
ENTRYPOINT ["python", "run.py"]