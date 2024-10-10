from aiokafka import AIOKafkaProducer
from pydantic import BaseModel
from .topics import Topic
from .config import get_kafka_configuration

class KafkaProducer:
    producer: AIOKafkaProducer
    
    async def __aenter__(self):
        config = get_kafka_configuration()
        self.producer = AIOKafkaProducer(**config)
        await self.producer.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.producer.stop()
    
    async def produce_message(self, topic: Topic, message: BaseModel) -> None:
        await self.producer.send_and_wait(topic.value, message.model_dump_json().encode("utf-8"))