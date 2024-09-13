import uuid
from domain.schema.courses.exercise import CourseExerciseBase, CourseExerciseObjectiveBase

class ExerciseObjectiveDto(CourseExerciseObjectiveBase):
    objective: str

class ExerciseDto(CourseExerciseBase):
    id: uuid.UUID
    title: str
    summary: str
    environment_id: uuid.UUID
    objectives: list[ExerciseObjectiveDto]