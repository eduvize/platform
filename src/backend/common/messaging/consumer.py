import json
import logging
from time import sleep
from typing import Generator, Tuple, Type, TypeVar
from confluent_kafka import Consumer, KafkaError, KafkaException, Message
from pydantic import BaseModel
from .topics import Topic
from .config import get_kafka_configuration

T = TypeVar("T")

class KafkaConsumer:
    consumer: Consumer
    
    def __init__(self, topic: Topic, group_id: str) -> None:
        kafka_config = get_kafka_configuration()
        self.consumer = Consumer({
            **kafka_config,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False
        })
        
        self.consumer.subscribe([topic.value])
        
    def messages(self, message_type: Type[T]) -> Generator[Tuple[T, Message], None, None]:
        logging.info("Starting consumer...")
        
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logging.warning(f"Reached end of partition {msg.partition()}")
                        continue
                    elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                        logging.warning(f"Topic {msg.topic()} does not exist. Waiting before retry...")
                        sleep(5)
                        logging.warning(f"Retrying; subscribing to topic {msg.topic()}")
                        self.consumer.subscribe([msg.topic()])
                        continue
                    else:
                        raise KafkaException(msg.error())
                    
                else:
                    logging.info(f"Received message: {msg.key()}")
                    
                    # Read the JSON data, converting it to the specified type, and yield it
                    data = json.loads(msg.value())
                    
                    if issubclass(message_type, BaseModel):
                        model_instance = message_type.model_validate(data)
                    else:
                        model_instance = message_type(**data)
                    
                    yield model_instance, msg
        except KeyboardInterrupt:
            pass
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            logging.warning("Closing consumer...")
            self.consumer.close()
            
    def commit(self, message: Message) -> None:
        self.consumer.commit(message=message)