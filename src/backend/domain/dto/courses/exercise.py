import uuid
from domain.schema.courses.exercise import CourseExerciseBase, CourseExerciseObjectiveBase

class ExerciseObjectiveDto(CourseExerciseObjectiveBase):
    id: uuid.UUID
    objective: str
    description: str
    is_completed: bool

class ExerciseDto(CourseExerciseBase):
    id: uuid.UUID
    title: str
    summary: str
    environment_id: uuid.UUID
    objectives: list[ExerciseObjectiveDto]
    
class InternalExerciseObjectiveDto(CourseExerciseObjectiveBase):
    id: uuid.UUID
    objective: str
    description: str
    test_plan: str
    is_completed: bool
    
class InternalExerciseDto(CourseExerciseBase):
    id: uuid.UUID
    title: str
    summary: str
    objectives: list[InternalExerciseObjectiveDto]