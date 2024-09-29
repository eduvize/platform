from pydantic import BaseModel

class ExerciseObjectivePlan(BaseModel):
    objective: str
    description: str
    test_plan: str

class ExercisePlan(BaseModel):
    detailed_summary: str
    title: str
    docker_base_image: str
    initial_environment_state_expected: str
    objectives: list[ExerciseObjectivePlan]