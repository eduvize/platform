import logging
import multiprocessing
from .handle_environment_created import listen_for_environment_created_events
from .handle_environment_build_failure import listen_for_environment_build_failure_events
from .handle_course_generated import listen_for_course_generated_events

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    course_generated_process = multiprocessing.Process(target=listen_for_course_generated_events)
    environment_created_process = multiprocessing.Process(target=listen_for_environment_created_events)
    environment_build_failure_process = multiprocessing.Process(target=listen_for_environment_build_failure_events)
    
    course_generated_process.start()
    environment_created_process.start()
    environment_build_failure_process.start()
    
    course_generated_process.join()
    environment_created_process.join()
    environment_build_failure_process.join()