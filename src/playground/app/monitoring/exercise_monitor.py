import logging
import time
import uuid
from .exercise_validation import validate_objective, stop_validation
from .api import get_exercise, set_exercise_objective_status
from .decoration import debounce
from app.filesystem import DirectoryMonitor
from socketio import Client
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)

exercise_id = None
socket_client: Client = None
start_time = time.time()

def run_exercise_monitor(sio_client: Client, e_id: uuid.UUID):
    global watcher, exercise_id, socket_client, start_time
    
    start_time = time.time()
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
    
    global start_time
    
    # Make sure its been at least 5 seconds since start
    if time.time() - start_time < 5:
        logging.info("Ignoring filesystem change due to startup")
        return

    validate_exercise_state()

def handle_shell_command(command: str):
    logging.info(f"Shell command received: {command}")
    
    global start_time
    
    # Make sure its been at least 5 seconds since start
    if time.time() - start_time < 5:
        logging.info("Ignoring filesystem change due to startup")
        return
    
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
    
    futures = []
    for objective in exercise.objectives:
        if objective.is_completed:
            continue
        
        future = executor.submit(validate_objective_state, exercise, objective)
        futures.append(future)
        
    for future in futures:
        future.result()

watcher = DirectoryMonitor(
    directory="/userland",
    callback=handle_filesystem_change,
    no_path_filter=True,
    trigger_on_modified=True
)

def validate_objective_state(exercise, objective):
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
            "is_completed": False })