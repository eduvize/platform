import logging
from app.repositories import PlaygroundRepository
from common.messaging import Topic, KafkaConsumer
from domain.topics import EnvironmentCreatedTopic

def listen_for_environment_created_events():
    """
    Listens for events that indicate a playground image has been built and is ready to add to the exercise entity.
    """
    logging.info("Listening for environment created events")
    
    playground_repo = PlaygroundRepository()

    consumer = KafkaConsumer(
        topic=Topic.ENVIRONMENT_CREATED,
        group_id="exercise-generator-environment-created"
    )

    for data, message in consumer.messages(message_type=EnvironmentCreatedTopic):
        try:
            logging.info(f"Received environment created event: {data.resource_id}, purpose: {data.purpose}")
            
            if not data.purpose == "exercise":
                logging.error(f"Not interested in purpose, skipping: {data.purpose}")
                consumer.commit(message)
                continue
            
            logging.info(f"Setting environment image tag: {data.image_tag} for environment: {data.resource_id}")
            playground_repo.set_environment_image_tag(
                environment_id=data.resource_id,
                image_tag=data.image_tag
            )
            
            consumer.commit(message)
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            consumer.commit(message)