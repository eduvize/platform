import logging
from app.repositories import PlaygroundRepository, CourseRepository
from common.messaging import Topic, KafkaConsumer
from domain.topics import EnvironmentBuildFailedTopic

def listen_for_environment_build_failure_events():
    """
    Listens for events that indicate a playground image could not be built successfully.
    """
    logging.info("Listening for environment build failure events")
    
    playground_repo = PlaygroundRepository()
    course_repo = CourseRepository()

    consumer = KafkaConsumer(
        topic=Topic.ENVIRONMENT_BUILD_FAILED,
        group_id="exercise-generator-environment-build-failed"
    )

    for data, message in consumer.messages(message_type=EnvironmentBuildFailedTopic):
        try:
            logging.info(f"Received environment creation failed event: {data.environment_id}, purpose: {data.purpose}")
            
            if not data.purpose == "exercise":
                logging.error(f"Not interested in purpose, skipping: {data.purpose}")
                consumer.commit(message)
                continue
            
            exercise = course_repo.get_exercise_by_environment(data.environment_id)
            
            if exercise is None:
                logging.error(f"Exercise not found for environment: {data.environment_id}. Skipping...")
                consumer.commit(message)
                continue
            
            logging.info("Removing exercise and environment records")
            course_repo.remove_exercise(exercise.id)
            playground_repo.remove_environment(data.environment_id)
            
            consumer.commit(message)
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            consumer.commit(message)