import json
import logging
import time
from typing import Generator, Tuple, Type, TypeVar

from confluent_kafka import Consumer, KafkaError, KafkaException, Message
from pydantic import BaseModel

from .topics import Topic
from .config import get_kafka_configuration

T = TypeVar("T")


class KafkaConsumer:
    consumer: Consumer
    topic: str
    group_id: str

    def __init__(self, topic: Topic, group_id: str) -> None:
        self.topic = topic.value
        self.group_id = group_id
        self.kafka_config = get_kafka_configuration()
        self.consumer = None
        self._connect_consumer()

    def _connect_consumer(self) -> None:
        retry_attempts = 0
        max_retries = 30
        while True:
            try:
                self.consumer = Consumer(
                    {
                        **self.kafka_config,
                        "group.id": self.group_id,
                        "auto.offset.reset": "earliest",
                        "enable.auto.commit": False,
                    }
                )
                self.consumer.subscribe([self.topic])
                logging.info(f"Consumer subscribed to topic {self.topic}")
                break
            except KafkaException as e:
                logging.error(f"Failed to create consumer: {e}")
                retry_attempts += 1
                if retry_attempts >= max_retries:
                    logging.error("Max retries reached. Exiting...")
                    raise
                sleep_time = 2 ** retry_attempts
                logging.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                raise

    def messages(
        self, message_type: Type[T]
    ) -> Generator[Tuple[T, Message], None, None]:
        logging.info("Starting consumer...")

        try:
            while True:
                try:
                    msg = self.consumer.poll(timeout=1.0)

                    if msg is None:
                        continue

                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            logging.warning(
                                f"Reached end of partition {msg.partition()}"
                            )
                            continue
                        elif msg.error().code() in (
                            KafkaError._ALL_BROKERS_DOWN,
                            KafkaError._TRANSPORT,
                        ):
                            logging.error(f"Kafka broker error: {msg.error()}")
                            self._handle_disconnect()
                            continue
                        elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                            logging.warning(
                                f"Topic {msg.topic()} does not exist. Waiting before retry..."
                            )
                            time.sleep(5)
                            logging.warning(
                                f"Retrying; subscribing to topic {msg.topic()}"
                            )
                            self.consumer.subscribe([msg.topic()])
                            continue
                        else:
                            raise KafkaException(msg.error())

                    else:
                        key = msg.key()
                        logging.info(f"Received message: {key}")

                        # Read the JSON data, converting it to the specified type, and yield it
                        data = json.loads(msg.value())

                        try:
                            if issubclass(message_type, BaseModel):
                                model_instance = message_type.model_validate(data)
                            else:
                                model_instance = message_type(**data)
                        except Exception as e:
                            logging.error(
                                f"An error occurred while validating the message: {e}. Skipping..."
                            )

                            # Write offset
                            self.consumer.commit(message=msg)

                            continue

                        yield model_instance, msg
                except KafkaException as e:
                    logging.error(f"Kafka exception occurred: {e}")
                    self._handle_disconnect()
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
                    self._handle_disconnect()
        except KeyboardInterrupt:
            pass
        finally:
            logging.warning("Closing consumer...")
            self.consumer.close()

    def _handle_disconnect(self) -> None:
        logging.warning("Handling disconnection...")
        self.consumer.close()
        time.sleep(5)
        logging.info("Reconnecting consumer...")
        self._connect_consumer()

    def commit(self, message: Message) -> None:
        self.consumer.commit(message=message)
