from typing import List, Optional
import uuid
from sqlmodel import SQLModel, Field, Relationship
import domain.schema as schema

class CourseExerciseObjectiveBase(SQLModel):
    objective: str = Field(nullable=False)
    
class CourseExerciseObjective(CourseExerciseObjectiveBase, table=True):
    __tablename__ = "course_exercise_objectives"
    
    id: uuid.UUID           = Field(default_factory=uuid.uuid4, primary_key=True)
    exercise_id: uuid.UUID  = Field(foreign_key="course_exercises.id")
    
    exercise: "schema.courses.exercise.CourseExercise" = Relationship(back_populates="objectives")

class CourseExerciseBase(SQLModel):
    title: str = Field(nullable=False)
    summary: str = Field(nullable=False)
    
class CourseExercise(CourseExerciseBase, table=True):
    __tablename__ = "course_exercises"
    
    id: uuid.UUID                           = Field(default_factory=uuid.uuid4, primary_key=True)
    lesson_id: uuid.UUID                    = Field(foreign_key="course_lessons.id")
    environment_id: uuid.UUID               = Field(foreign_key="playground_environments.id")
    lesson: "schema.courses.lesson.Lesson"  = Relationship(back_populates="exercises")
    objectives: List[CourseExerciseObjective] = Relationship(back_populates="exercise")