import logging
import asyncio
import multiprocessing
from .handle_environment_created import listen_for_environment_created_events
from .handle_environment_build_failure import listen_for_environment_build_failure_events
from .handle_course_generated import listen_for_course_generated_events

logging.basicConfig(level=logging.INFO)

def run_consumer(consumer_func):
    """
    Wrapper function to run a consumer in a separate process.
    """
    asyncio.run(consumer_func())

async def main():
    """
    Main function to run all Kafka consumers concurrently in separate processes.
    """
    consumers = [
        listen_for_course_generated_events,
        listen_for_environment_created_events,
        listen_for_environment_build_failure_events
    ]

    processes = []
    try:
        for consumer in consumers:
            process = multiprocessing.Process(target=run_consumer, args=(consumer,))
            process.start()
            processes.append(process)

        # Wait for all processes to complete (which they won't, as they run indefinitely)
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt. Shutting down...")
    finally:
        # Terminate all processes
        for process in processes:
            process.terminate()
        
        # Wait for all processes to finish terminating
        for process in processes:
            process.join()
        
        logging.info("All consumers have been shut down.")

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    asyncio.run(main())