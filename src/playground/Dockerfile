# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that your FastAPI app will run on
EXPOSE ${PORT}

# Set the environment variable PORT with a default value of 5000
ENV PORT=5000

# Command to run the application
CMD ["python", "run.py"]