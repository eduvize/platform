# This Dockerfile should be run from the same context as the primary backend app Dockerfile.
# The JOB_NAME argument must be passed to copy over the correct job code into the container.
# Several pieces of the main backend codebase will be copied over to the container to ensure the job runs correctly.

# Use an official Python runtime as a parent image
FROM python:3.9-slim

ARG JOB_NAME

# Set the working directory in the container
WORKDIR /app

# Update system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    python3-dev \
    poppler-utils

# Copy over the job requirements
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy over shared packages
COPY ai ai
COPY common common
COPY domain domain

# Copy over partial pieces of the primary backend app
COPY config.py config.py
COPY app/repositories app/repositories
COPY app/utilities app/utilities

# Copy the job code into the container at /app
COPY jobs/${JOB_NAME} .

# Run the main entrypoint for the specific job
ENTRYPOINT [ "python", "main.py" ]