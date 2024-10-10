import logging
import asyncio
from ai.prompts import GenerateModuleContentPrompt
from app.repositories import CourseRepository
from common.messaging import Topic, KafkaConsumer, KafkaProducer
from domain.topics import CourseGenerationTopic, CourseGeneratedTopic
from domain.dto.courses import CourseDto

logging.basicConfig(level=logging.INFO)

repository = CourseRepository()

producer = KafkaProducer()

consumer = KafkaConsumer(
    topic=Topic.GENERATE_NEW_COURSE,
    group_id="course_generator"
)

def calculate_total_section_count(course_outline):
    """Calculate the total number of sections in the course outline."""
    return sum(
        len(lesson.sections)
        for module in course_outline.modules
        for lesson in module.lessons
    )

class ProgressCallback:
    def __init__(self, progress_queue):
        self.progress_queue = progress_queue

    async def __call__(self, progress):
        # Asynchronously put the progress update into the queue
        await self.progress_queue.put(progress)

async def generate_module(data, module, progress_queue):
    """Generate content for a single module."""
    # Create a progress callback instance for this module
    progress_cb = ProgressCallback(progress_queue)

    module_prompt = GenerateModuleContentPrompt()
    # Generate module content, passing the progress callback
    module_dto = await module_prompt.generate_module_content(
        course=data.course_outline,
        module=module,
        progress_cb=progress_cb
    )
    logging.info(f"Generated module '{module_dto.title}'")
    return module_dto

async def generate_course(data):
    """Generate the entire course content."""
    total_section_count = calculate_total_section_count(data.course_outline)
    progress_queue = asyncio.Queue()
    course_dto = CourseDto.model_construct(modules=[])

    # Progress monitor coroutine
    async def progress_monitor():
        sections_completed = 0
        while True:
            try:
                # Wait for a progress update with a timeout
                update = await asyncio.wait_for(progress_queue.get(), timeout=1.0)
                if update is None:
                    # None is used as a signal to stop the monitor
                    break
                # Increment the completed sections count
                sections_completed += 1
                # Calculate percentage based on completed sections
                percentage = int((sections_completed / total_section_count) * 100)
                # Update the progress in the repository
                await repository.set_generation_progress(
                    course_id=data.course_id,
                    progress=percentage
                )
                logging.info(f"Progress updated: {percentage}%")
            except asyncio.TimeoutError:
                # If no update received within timeout, continue waiting
                continue

    # Start the progress monitor as a separate task
    monitor_task = asyncio.create_task(progress_monitor())

    # Use asyncio.Semaphore to limit concurrency
    semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent tasks

    async def generate_module_with_semaphore(module):
        # Use semaphore to limit concurrent module generations
        async with semaphore:
            return await generate_module(data, module, progress_queue)

    # Create tasks for each module
    module_tasks = [
        generate_module_with_semaphore(module)
        for module in data.course_outline.modules
    ]

    # Wait for all module generation tasks to complete
    modules_dto = await asyncio.gather(*module_tasks)

    # Append modules to course_dto in order
    course_dto.modules.extend(modules_dto)

    # Signal the monitor coroutine to exit
    await progress_queue.put(None)
    await monitor_task  # Wait for the monitor to finish

    logging.info(f"Generated course content for '{data.course_outline.course_title}'")
    logging.info("Creating course content in the database...")

    # Create the course content in the database
    await repository.create_course_content(
        course_id=data.course_id,
        course_dto=course_dto
    )
    
    logging.info("Course content created successfully")

# Continuously iterate over incoming course generation jobs
async def main():   
    for data, message in consumer.messages(message_type=CourseGenerationTopic):
        logging.info(f"Received course generation job: {data.course_outline.course_title}, id: {data.course_id}")

        try:
            await generate_course(data)

            logging.info("Producing course generated event...")

            # Notify the system that the course has been generated
            await producer.produce_message(
                topic=Topic.COURSE_GENERATED,
                message=CourseGeneratedTopic(
                    user_id=data.user_id,
                    course_id=data.course_id
                )
            )

            # Commit the message to the Kafka topic offset
            consumer.commit(message)
        except Exception as e:
            logging.error(f"Failed to generate course content: {e}. Skipping...")
            consumer.commit(message)

if __name__ == '__main__':
    asyncio.run(main())