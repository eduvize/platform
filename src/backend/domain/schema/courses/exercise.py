from sqlmodel import SQLModel

class ExerciseBase(SQLModel):
    description: str