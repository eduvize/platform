import os
from typing import Literal


def get_kafka_configuration(usage: Literal["producer", "consumer"]) -> dict:
    if usage == "consumer":
        return {
            "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
            "max.poll.interval.ms": int(os.getenv("KAFKA_MAX_POLL_INTERVAL_SECONDS", "300")) * 1000,
            "acks": "all"
        }
        
    return {
        "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        "acks": "all"
    }