import logging
import uuid
from ai.prompts import GenerateExercisesPrompt, SelectExerciseLessonsPrompt
from app.repositories import CourseRepository, PlaygroundRepository
from common.messaging import Topic, KafkaConsumer, KafkaProducer
from domain.topics import CourseGeneratedTopic, BuildPlaygroundTopic
from domain.dto.courses.exercise_plan import ExercisePlan

async def create_exercise(
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
    environment_id = await playground_repo.create_environment(
        user_id=user_id,
        docker_base_image=exercise.docker_image,
        description=exercise.scenario
    )
    logging.info(f"Environment created: {environment_id}")

    # Create the exercise
    logging.info("Creating exercise record")
    exercise_id = await course_repo.create_exercise(
        lesson_id=lesson_id,
        environment_id=environment_id,
        title=exercise.title,
        summary=exercise.scenario,
        objectives=exercise.objectives
    )
    logging.info(f"Exercise created: {exercise_id}")
    
    # Send event to playground environment builder
    logging.info("Sending build playground event")
    await producer.produce_message(
        topic=Topic.BUILD_PLAYGROUND,
        message=BuildPlaygroundTopic(
            purpose="exercise",
            environment_id=environment_id,
            resource_id=exercise_id,
            data=exercise
        )
    )
    
    logging.info("Sent build playground event")

async def listen_for_course_generated_events():
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
            logging.info(f"Getting course: {data.course_id}")
            course = await course_repo.get_course(data.course_id)
            
            if course is None:
                logging.info(f"Course not found: {data.course_id}. Skipping...")
                consumer.commit(message)
                continue
            
            logging.info(f"Course found: {course.title}")
            
            # Log course details
            logging.info(f"Course modules: {len(course.modules)}")
            total_lessons = sum([len(module.lessons) for module in course.modules])
            logging.info(f"Total lessons: {total_lessons}")
            
            logging.info("Selecting lessons to generate exercises for")
            lessons_to_generate = await SelectExerciseLessonsPrompt().get_best_lessons(course, max_lessons=total_lessons / 2)
            
            num_lessons_to_generate = len(lessons_to_generate)
            logging.info(f"Selected {num_lessons_to_generate} lessons to generate exercises for")
            
            # Iterate over each lesson in each module to generate potential exercises
            for index, lesson in enumerate(lessons_to_generate, 1):
                try:
                    logging.info(f"Generating exercises for lesson {index}/{num_lessons_to_generate}: {lesson.title}")
                    
                    lesson_content = "\n".join([
                        section.content
                        for section in lesson.sections
                    ])
                    
                    lesson_content = f"""
Course: {course.title}
Current Lesson: {lesson.title}
Lesson Description: {lesson.description}

Lesson content:
{lesson_content}                 
"""
                    
                    prompt = GenerateExercisesPrompt()
                    logging.info(f"Calling AI to generate exercise for lesson: {lesson.title}")
                    lesson_exercise = await prompt.get_exercise(lesson_content)
                    
                    if lesson_exercise:
                        logging.info(f"Exercise generated for lesson: {lesson.title}")
                        await create_exercise(
                            user_id=course.user_id,
                            exercise=lesson_exercise,
                            lesson_id=lesson.id,
                            producer=producer,
                            course_repo=course_repo,
                            playground_repo=playground_repo
                        )
                    else:
                        logging.warning(f"No exercise generated for lesson: {lesson.title}")
                except Exception as e:
                    logging.error(f"Failed to generate exercises for lesson: {lesson.title}. Error: {str(e)}")
                    continue
            
            logging.info(f"Finished processing course: {data.course_id}")
            # Commit the message to the Kafka topic offset
            consumer.commit(message)
        except ValueError as e:
            logging.error(f"Failed to generate course content: {str(e)}. Skipping...")
            consumer.commit(message)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}. Not committing message...")