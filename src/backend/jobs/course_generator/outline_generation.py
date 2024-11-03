import logging
from ai.prompts import GenerateCourseOutlinePrompt
from app.repositories import CourseRepository
from common.messaging import Topic, KafkaConsumer, KafkaProducer
from domain.topics import CourseCreatedTopic, CourseGenerationTopic

logging.basicConfig(level=logging.INFO)

repository = CourseRepository()

consumer = KafkaConsumer(
    topic=Topic.COURSE_CREATED,
    group_id="new_course_outline_generator"
)

async def listen_for_course_creation_jobs():
    for data, message in consumer.messages(message_type=CourseCreatedTopic):
        logging.info(f"Received new course creation job: {data.course_title}, id: {data.course_id}")

        try:
            # Generate a course outline based on user requirements and profile
            prompt = GenerateCourseOutlinePrompt()
            outline = await prompt.get_outline(
                course_title=data.course_title,
                course_summary=data.course_description,
                key_outcomes=data.key_outcomes,
                topics=data.topics
            )

            logging.info("Producing generate course job...")

            # Notify the system that the course has been generated
            async with KafkaProducer() as producer:
                await producer.produce_message(
                    topic=Topic.GENERATE_NEW_COURSE,
                    message=CourseGenerationTopic(
                        user_id=data.user_id,
                        course_id=data.course_id,
                        course_outline=outline
                    )
                )

            # Commit the message to the Kafka topic offset
            consumer.commit(message)
        except Exception as e:
            logging.error(f"Failed to generate course outline: {e}")
