##
## This Dockerfile utilizes Docker-in-Docker to run a custom playground environment for a user to run their code in.
##

FROM docker:dind
ENV REGISTRY=""
ENV REGISTRY_USER=""
ENV REGISTRY_CRED=""

# Install dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-setuptools \
    py3-wheel

# Install a virtual environment
RUN python3 -m venv /env

# Set the environment path
ENV PATH="/env/bin:$PATH"

# Copy the requirements file
COPY requirements.txt .

# Install the requirements
RUN pip3 install -r requirements.txt

WORKDIR /app
COPY app .

WORKDIR /
COPY container-entrypoint.sh /container-entrypoint.sh
RUN chmod +x /container-entrypoint.sh

# Run the entrypoint
CMD ["sh", "-c", "/container-entrypoint.sh"]