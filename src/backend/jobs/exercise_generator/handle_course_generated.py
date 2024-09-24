import logging
import uuid
from ai.prompts import GenerateExercisesPrompt
from app.repositories import CourseRepository, PlaygroundRepository
from common.messaging import Topic, KafkaConsumer, KafkaProducer
from domain.topics import CourseGeneratedTopic, BuildPlaygroundTopic
from domain.dto.courses.exercise_plan import ExercisePlan

def create_exercise(
    user_id: uuid.UUID, 
    exercise: ExercisePlan, 
    lesson_id: uuid.UUID,
    producer: KafkaProducer, 
    course_repo: CourseRepository,
    playground_repo: PlaygroundRepository
):
    logging.info(f"Generated exercise: {exercise.title}")

    # Create an environment for the exercise
    logging.info("Creating environment record for exercise")
    environment_id = playground_repo.create_environment(
        user_id=user_id,
        docker_base_image=exercise.docker_base_image,
        description=exercise.initial_environment_state_expected
    )
    logging.info(f"Environment created: {environment_id}")

    # Create the exercise
    logging.info("Creating exercise record")
    exercise_id = course_repo.create_exercise(
        lesson_id=lesson_id,
        environment_id=environment_id,
        title=exercise.title,
        summary=exercise.detailed_summary,
        objectives=exercise.objectives
    )
    logging.info(f"Exercise created: {exercise_id}")
    
    # Send event to playground environment builder
    logging.info("Sending build playground event")
    producer.produce_message(
        topic=Topic.BUILD_PLAYGROUND,
        message=BuildPlaygroundTopic(
            purpose="exercise",
            environment_id=environment_id,
            resource_id=exercise_id,
            base_image=exercise.docker_base_image,
            description=exercise.initial_environment_state_expected
        )
    )
    
    logging.info("Sent build playground event")

def listen_for_course_generated_events():
    """
    Listens for events that indicate a new course has been generated and then generates exercises for each lesson in the course if applicable.
    
    This consumer will produce an event for each environment, requesting a new image to be built for the exercise.
    """
    logging.info("Listening for course generated events")
    
    producer = KafkaProducer()
    playground_repo = PlaygroundRepository()
    course_repo = CourseRepository()

    consumer = KafkaConsumer(
        topic=Topic.COURSE_GENERATED,
        group_id="exercise-generator"
    )

    for data, message in consumer.messages(message_type=CourseGeneratedTopic):
        logging.info(f"Received course generated event, id: {data.course_id}")
        
        try:
            # Get the course
            course = course_repo.get_course(data.course_id)
            
            if course is None:
                logging.error(f"Course not found: {data.course_id}. Skipping...")
                consumer.commit(message)
                continue
            
            # Iterate over each lesson in each module to generate potential exercises
            for module in course.modules:
                logging.info(f"Generating exercises for module: {module.title}")
                
                for lesson in module.lessons:
                    logging.info(f"Generating exercises for lesson: {lesson.title}")
                    
                    lesson_content = "\n".join([
                        section.content
                        for section in lesson.sections
                    ])
                    
                    lesson_content = f"""
Course: {course.title}
Current Module: {module.title}
Current Lesson for Exercise: {lesson.title}

Lesson content:
{lesson_content}                 
"""
                    
                    prompt = GenerateExercisesPrompt()
                    lesson_exercise = prompt.get_exercise(lesson_content)
                    
                    if lesson_exercise:
                        create_exercise(
                            user_id=course.user_id,
                            exercise=lesson_exercise,
                            lesson_id=lesson.id,
                            producer=producer,
                            course_repo=course_repo,
                            playground_repo=playground_repo
                        )
                    
            # Commit the message to the Kafka topic offset
            consumer.commit(message)
        except ValueError as e:  # TODO: This should specifically look for a course not existing rather than a generic ValueError
            logging.error(f"Failed to generate course content: {e}. Skipping...")
            consumer.commit(message)
