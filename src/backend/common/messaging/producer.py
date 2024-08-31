import json
from confluent_kafka import Producer
from pydantic import BaseModel
from .topics import Topic
from .config import get_kafka_configuration

class KafkaProducer:
    producer: Producer
    
    def __init__(self) -> None:
        config = get_kafka_configuration()
        self.producer = Producer(**config)
        
    def produce_message(self, topic: Topic, message: BaseModel) -> None:
        self.producer.produce(topic.value, value=message.model_dump_json().encode("utf-8"))
        self.producer.flush()