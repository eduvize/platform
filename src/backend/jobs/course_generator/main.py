import logging
import multiprocessing
from multiprocessing import Pool, Manager
import threading
from itertools import repeat

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

    def __call__(self, lindex):
        self.progress_queue.put(1)  # Send a progress update to the main process

def generate_module(args):
    """Generate content for a single module."""
    data, module, progress_queue = args

    progress_cb = ProgressCallback(progress_queue)

    module_prompt = GenerateModuleContentPrompt()
    module_dto = module_prompt.generate_module_content(
        course=data.course_outline,
        module=module,
        progress_cb=progress_cb
    )
    logging.info(f"Generated module '{module_dto.title}'")
    return module_dto

def generate_course(data):
    """Generate the entire course content."""
    total_section_count = calculate_total_section_count(data.course_outline)
    manager = Manager()
    progress_queue = manager.Queue()
    course_dto = CourseDto.model_construct(modules=[])

    # Progress monitor thread
    def progress_monitor():
        current_section = 0
        while True:
            item = progress_queue.get()
            if item is None:
                break
            current_section += item
            progress = int((current_section / total_section_count) * 100)
            repository.set_generation_progress(
                course_id=data.course_id,
                progress=progress
            )

    monitor_thread = threading.Thread(target=progress_monitor)
    monitor_thread.start()

    # Limit the number of processes to 3
    pool = Pool(processes=3)
    try:
        # Prepare arguments for each module
        args_iterable = [
            (data, module, progress_queue)
            for module in data.course_outline.modules
        ]

        # Use starmap to maintain the order of modules
        modules_dto = pool.map(generate_module, args_iterable)

        # Append modules to course_dto in order
        course_dto.modules.extend(modules_dto)
    except Exception as e:
        logging.error(f"Error generating modules in parallel: {e}.")
        raise  # Re-raise the exception to handle it appropriately
    finally:
        pool.close()
        pool.join()
        progress_queue.put(None)  # Signal the monitor thread to exit
        monitor_thread.join()

    logging.info(f"Generated course content for '{data.course_outline.course_title}'")
    logging.info("Creating course content in the database...")

    # Create the course content in the database
    repository.create_course_content(
        course_id=data.course_id,
        course_dto=course_dto
    )
    
    logging.info("Course content created successfully")

# Continuously iterate over incoming course generation jobs
for data, message in consumer.messages(message_type=CourseGenerationTopic):
    logging.info(f"Received course generation job: {data.course_outline.course_title}, id: {data.course_id}")

    try:
        generate_course(data)

        logging.info("Producing course generated event...")

        # Notify the system that the course has been generated
        producer.produce_message(
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
