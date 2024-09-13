from pydantic import BaseModel

class ExercisePlan(BaseModel):
    title: str
    summary: str
    objectives: list[str]
    docker_base_image: str
    initial_environment_state_expected: str