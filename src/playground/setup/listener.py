import time
import json
import logging
import os
from confluent_kafka import Consumer, KafkaError, Producer
from .builder import build_exercise_image, BuildException
from .models import ExercisePlan

logging.basicConfig(level=logging.INFO)

# Configuration for the consumer
consumer_config = {
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    'max.poll.interval.ms': 1800000,
    'group.id': 'playground-builder',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False  # Disable auto commit
}

producer_config = {
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
}

consumer = Consumer(consumer_config)
producer = Producer(producer_config)

# Retry delay in seconds (you can configure this as needed)
RETRY_DELAY = 10

def subscribe_to_topic(consumer):
    """Subscribe to the Kafka topic and handle retries if the topic is unavailable."""
    while True:
        try:
            logging.info("Subscribing to the 'build_playground' topic")
            consumer.subscribe(['build_playground'])
            return  # Exit the loop if the subscription is successful
        except KafkaError as e:
            if e.args[0].code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                logging.error("Kafka topic 'build_playground' not available. Retrying in 10 seconds...")
            else:
                logging.error(f"Kafka error: {e}")
        
        time.sleep(RETRY_DELAY)

        logging.info("Retrying subscription...")

# Poll for messages in a loop
def poll_messages(consumer):
    logging.info("Polling for messages")
    try:
        while True:
            # Poll for a message (wait up to 1 second)
            message = consumer.poll(timeout=1.0)

            # If no message, continue the loop
            if message is None:
                continue

            # If there's an error in the message
            if message.error():
                # Handle the end of partition case
                if message.error().code() == KafkaError._PARTITION_EOF:
                    logging.info(f"Reached end of partition {message.partition()} at offset {message.offset()}")
                else:
                    logging.error(f"Error: {message.error()}")
                    
                    if message.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                        # Topic not found, retry after a delay
                        time.sleep(RETRY_DELAY)
                        
                        # Resubscribe to the topic
                        subscribe_to_topic(consumer)
            else:
                # Successfully received a message, print the value
                logging.info(f"Received message: {message.value().decode('utf-8')} from topic: {message.topic()} partition: {message.partition()} offset: {message.offset()}")

                # Load the message as json
                data = json.loads(message.value().decode("utf-8"))

                purpose = data.get("purpose", None) # The purpose of the environment (i.e exercise)
                environment_id = data.get("environment_id", None) # The ID of the environment this image is for
                resource_id = data.get("resource_id", None) # The ID of the resource this environment is associated to (i.e exercise)
                exercise_plan: dict = data.get("data", None) # The exercise plan data

                try:
                    exercise_plan: ExercisePlan = ExercisePlan.model_validate(exercise_plan)
                except Exception as e:
                    logging.error(f"Invalid exercise plan data: {e}")
                    
                    # Commit the offset
                    consumer.commit(message=message)
                    
                    continue

                # Build the image
                try:
                    tag = build_exercise_image(
                        exercise=exercise_plan,
                    )
                    
                    if tag:
                        # Publish environment created event
                        producer.produce(
                            topic="environment_created",
                            value=json.dumps({
                                "purpose": purpose,
                                "environment_id": environment_id,
                                "resource_id": resource_id,
                                "image_tag": tag
                            })
                        )
                    else:
                        logging.error("Failed to build the image. Reporting failure")
                        
                        producer.produce(
                            topic="environment_build_failed",
                            value=json.dumps({
                                "purpose": purpose,
                                "environment_id": environment_id
                            })   
                        )
                except BuildException as e:
                    logging.error(f"Failed to build the image: {e}")

                    # Report the failure
                    producer.produce(
                        topic="environment_build_failed",
                        value=json.dumps({
                            "purpose": purpose,
                            "environment_id": environment_id,
                            "error": str(e)                        })
                    )       
                except Exception as e:
                    logging.error(f"An unexpected error occurred: {e}")
                    
                    # Report the failure
                    producer.produce(
                        topic="environment_build_failed",
                        value=json.dumps({
                            "purpose": purpose,
                            "environment_id": environment_id,
                            "error": str(e)
                        })
                    )
                finally:             
                    # Commit the offset
                    consumer.commit(message=message)

    except KeyboardInterrupt:
        # Gracefully exit on Ctrl+C
        pass
    finally:
        # Close the consumer gracefully
        consumer.close()

if __name__ == "__main__":
    subscribe_to_topic(consumer)
    poll_messages(consumer)
