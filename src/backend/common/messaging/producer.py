from aiokafka import AIOKafkaProducer
from pydantic import BaseModel
from typing import Optional
import logging
import asyncio
from .topics import Topic
from .config import get_kafka_configuration

class KafkaProducer:
    """
    Async Kafka producer with automatic retries and error handling.
    Uses context manager pattern for proper resource cleanup.
    """
    producer: Optional[AIOKafkaProducer] = None
    
    async def __aenter__(self):
        await self._connect_producer()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.producer:
            await self.producer.stop()
    
    async def _connect_producer(self, max_retries: int = 5) -> None:
        """
        Establishes connection to Kafka with retry logic.
        
        Args:
            max_retries (int): Maximum number of connection attempts
        """
        retry_count = 0
        while True:
            try:
                config = get_kafka_configuration("producer")
                self.producer = AIOKafkaProducer(**config)
                await self.producer.start()
                logging.info("Successfully connected to Kafka")
                break
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logging.error(f"Failed to connect to Kafka after {max_retries} attempts")
                    raise
                
                wait_time = min(2 ** retry_count, 30)  # Exponential backoff capped at 30 seconds
                logging.warning(f"Failed to connect to Kafka: {str(e)}. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
    
    async def produce_message(self, topic: Topic, message: BaseModel, max_retries: int = 3) -> None:
        """
        Produces a message to a Kafka topic with retry logic.
        
        Args:
            topic (Topic): The topic to produce to
            message (BaseModel): The Pydantic model to serialize and send
            max_retries (int): Maximum number of retry attempts for failed sends
        
        Raises:
            Exception: If message production fails after all retries
        """
        if not self.producer:
            raise RuntimeError("Producer not initialized. Use context manager 'with' statement.")
            
        retry_count = 0
        last_exception = None
        
        while retry_count < max_retries:
            try:
                value = message.model_dump_json().encode("utf-8")
                await self.producer.send_and_wait(topic.value, value)
                logging.debug(f"Successfully produced message to topic {topic.value}")
                return
            except Exception as e:
                retry_count += 1
                last_exception = e
                
                if retry_count < max_retries:
                    wait_time = min(2 ** retry_count, 30)
                    logging.warning(
                        f"Failed to produce message to topic {topic.value}. "
                        f"Attempt {retry_count}/{max_retries}. Retrying in {wait_time} seconds..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logging.error(
                        f"Failed to produce message to topic {topic.value} "
                        f"after {max_retries} attempts. Last error: {str(e)}"
                    )
        
        raise last_exception if last_exception else Exception("Failed to produce message")