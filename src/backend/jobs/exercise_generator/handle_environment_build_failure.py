import logging
from app.repositories import CourseRepository
from common.messaging import Topic, KafkaConsumer, KafkaProducer
from domain.topics import EnvironmentBuildFailedTopic, BuildPlaygroundTopic
from ai.prompts import GenerateExercisesPrompt

async def listen_for_environment_build_failure_events():
    """
    Listens for events that indicate a playground image could not be built successfully.
    """
    logging.info("Listening for environment build failure events")
    
    course_repo = CourseRepository()

    producer = KafkaProducer()
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
            
            exercise = await course_repo.get_exercise_by_environment(data.environment_id)
            
            if exercise is None:
                logging.error(f"Exercise not found for environment: {data.environment_id}. Skipping...")
                consumer.commit(message)
                continue
            
            await course_repo.set_exercise_setup_error(exercise_id=exercise.id, detail=data.error)
            
            if exercise.rebuild_attempts < 2 and data.error:
                # We'll attempt to rebuild the environment up to two times.
                # We will run the exercise generation prompt with the error data and use an updated plan.
                logging.info(f"Attempting to rebuild exercise due to errors: {exercise.id}")
                
                # Get the lesson
                lesson = await course_repo.get_lesson(exercise.lesson_id)
                
                # Take all content from data.error up to "Dockerfile content:" if it exists
                if "Dockerfile content:" in data.error:
                    error_content = data.error.split("Dockerfile content:")[0]
                else:
                    error_content = data.error
                
                new_plan = await GenerateExercisesPrompt().get_exercise(
                    lesson_content="\n".join([
                        section.content
                        for section in lesson.sections
                    ]),
                    previous_error=error_content
                )
                
                producer.produce_message(
                    topic=Topic.BUILD_PLAYGROUND,
                    message=BuildPlaygroundTopic(
                        purpose="exercise",
                        environment_id=data.environment_id,
                        resource_id=exercise.id,
                        data=new_plan
                    )
                )
                
                await course_repo.increment_exercise_build_attempts(exercise.id)
            
            consumer.commit(message)
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            consumer.commit(message)