from typing import Optional
from domain.dto.courses.exercise import ExerciseDto
from domain.schema.courses.lesson import LessonBase

class LessonDto(LessonBase):
    exercise: Optional[ExerciseDto] = None