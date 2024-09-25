import logging
import uuid
from .exercise_validation import validate_objective, stop_validation
from .api import get_exercise, set_exercise_objective_status
from .decoration import debounce
from app.filesystem import DirectoryMonitor
from socketio import Client

exercise_id = None
socket_client: Client = None

def run_exercise_monitor(sio_client: Client, e_id: uuid.UUID):
    global watcher, exercise_id, socket_client
    
    exercise_id = e_id
    socket_client = sio_client
    
    # Get the exercise
    exercise = get_exercise(exercise_id)

    if exercise is None:
        raise ValueError("Exercise not found")
    
    watcher = DirectoryMonitor(
        directory="/userland",
        callback=handle_filesystem_change,
        no_path_filter=True,
        trigger_on_modified=True
    )
    
    watcher.start_watching()

def stop_exercise_monitor():
    global watcher
    stop_validation()
    watcher.stop_watching()

def handle_filesystem_change(path: str):
    logging.info(f"Filesystem change detected at {path}")

    validate_exercise_state()

def handle_shell_command(command: str):
    logging.info(f"Shell command received: {command}")
    
    validate_exercise_state()

@debounce("validate_state", 5)
def validate_exercise_state():
    global exercise_id
    
    logging.info("Beginning validation on exercise objectives")
    
    # Get the most recent exercise data
    exercise = get_exercise(exercise_id)
    
    if exercise is None:
        logging.error("Exercise not found")
        raise ValueError("Exercise not found")
    
    for objective in exercise.objectives:
        if objective.is_completed:
            continue
        
        is_complete = validate_objective(exercise, objective)
        
        if is_complete:
            logging.info(f"Objective {objective.id} is complete")
            set_exercise_objective_status(exercise_id, objective.id, True)
            socket_client.emit("exercise_objective_status", {
                "objective_id": str(objective.id),
                "is_completed": True
            })
        else:
            logging.info(f"Objective {objective.id} is incomplete")
            set_exercise_objective_status(exercise_id, objective.id, False)
            socket_client.emit("exercise_objective_status", {
                "objective_id": str(objective.id),
                "is_completed": False
            })
    

watcher = DirectoryMonitor(
    directory="/userland",
    callback=handle_filesystem_change,
    no_path_filter=True,
    trigger_on_modified=True
)