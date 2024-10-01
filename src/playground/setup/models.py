from pydantic import BaseModel

class ExerciseObjectivePlan(BaseModel):
    objective: str
    description: str
    test_plan: str

class ExerciseFile(BaseModel):
    path: str
    content: str
    
class ExercisePlan(BaseModel):
    scenario: str
    title: str
    docker_image: str
    system_packages: list[str]
    files: list[ExerciseFile]
    objectives: list[ExerciseObjectivePlan]
    pre_commands: list[str]
    post_commands: list[str]