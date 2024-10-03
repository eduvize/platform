FROM docker:dind
ENV REGISTRY=""
ENV REGISTRY_USER=""
ENV REGISTRY_CRED=""

# Install dependencies
RUN apk add --no-cache \
    bash \
    python3 \
    py3-pip \
    py3-setuptools \
    py3-wheel \
    python3-dev \
    gcc \
    build-base \
    curl \
    openssl-dev \
    lz4-dev \
    cyrus-sasl-dev \
    zlib-dev

# Install librdkafka from source
ENV LIBRDKAFKA_VERSION="2.5.3"

RUN curl -L "https://github.com/edenhill/librdkafka/archive/refs/tags/v${LIBRDKAFKA_VERSION}.tar.gz" -o librdkafka.tar.gz && \
    tar -xzf librdkafka.tar.gz && \
    cd librdkafka-${LIBRDKAFKA_VERSION} && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf librdkafka-${LIBRDKAFKA_VERSION} librdkafka.tar.gz

WORKDIR /setup
COPY setup/requirements.txt .

# Create a virtual environment and activate it
RUN python3 -m venv /env
ENV PATH="/env/bin:$PATH"

# Upgrade pip to the latest version
RUN pip3 install --upgrade pip

# Install pip dependencies
RUN pip3 install -r requirements.txt

COPY setup/* .

WORKDIR /
COPY builder-entrypoint.sh /builder-entrypoint.sh
RUN chmod +x /builder-entrypoint.sh

# Run the entrypoint
CMD ["sh", "-c", "/builder-entrypoint.sh"]
