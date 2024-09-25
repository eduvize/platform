import uuid
import requests
from .models import InternalExerciseDto
from app.config import get_backend_api_endpoint, get_jwt_signing_key
from app.jwt import create_token

def get_exercise(exercise_id: uuid.UUID) -> InternalExerciseDto:
    """
    Retrieves an exercise from the API
    """
    endpoint = f"{get_backend_api_endpoint()}/courses/internal/exercises/{exercise_id}"
    token = create_token(data={}, secret=get_jwt_signing_key(), expiration_minutes=5)
    
    # Make a GET request to the API
    response = requests.get(endpoint, headers={"Authorization": f"Bearer {token}"})
    
    # Check if the request was successful
    if response.status_code == 200:
        return InternalExerciseDto(**response.json())

    raise ValueError(f"Failed to retrieve exercise: {response.text}")

def set_exercise_objective_status(exercise_id: uuid.UUID, objective_id: uuid.UUID, is_complete: bool) -> None:
    """
    Marks a given objective for an exercise as complete
    """
    endpoint = f"{get_backend_api_endpoint()}/courses/internal/exercises/{exercise_id}/objectives/{objective_id}/complete"
    token = create_token(data={}, secret=get_jwt_signing_key(), expiration_minutes=5)
    
    if is_complete:
        response = requests.post(endpoint, headers={"Authorization": f"Bearer {token}"}, json={})
    else:
        response = requests.delete(endpoint, headers={"Authorization": f"Bearer {token}"})
    
    # Check if the request was successful
    if response.status_code != 200:
        raise ValueError(f"Failed to mark objective status: {response.text}")