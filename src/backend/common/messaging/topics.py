from enum import Enum

class Topic(Enum):
    GENERATE_NEW_COURSE = "generate_new_course"
    BUILD_PLAYGROUND = "build_playground"
    COURSE_GENERATED = "course_generated"
    ENVIRONMENT_CREATED = "environment_created"
    ENVIRONMENT_BUILD_FAILED = "environment_build_failed"