import logging
import asyncio
from .handle_environment_created import listen_for_environment_created_events
from .handle_environment_build_failure import listen_for_environment_build_failure_events
from .handle_course_generated import listen_for_course_generated_events

logging.basicConfig(level=logging.INFO)

async def main():
    """
    Main function to run all async event listeners concurrently.
    """
    await asyncio.gather(
        listen_for_course_generated_events(),
        listen_for_environment_created_events(),
        listen_for_environment_build_failure_events()
    )

if __name__ == '__main__':
    asyncio.run(main())