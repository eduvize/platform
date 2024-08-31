import os


def get_kafka_configuration() -> dict:
    return {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        "max.poll.interval.ms": int(os.getenv("KAFKA_MAX_POLL_INTERVAL_SECONDS", "300")) * 1000,
        "acks": "all"
    }