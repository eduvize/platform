import logging
import subprocess

def reinitialize_environment():
    try:
        script_path = "/playground/entrypoint.sh"
        
        result = subprocess.run([script_path], capture_output=True, text=True, check=True, timeout=60)
        
        logging.info("Script output (stdout):")
        logging.info(result.stdout)
        
        if result.returncode == 0:
            logging.info("Environment reinitialized successfully")
        else:
            logging.error("Script execution failed with return code %d", result.returncode)
            logging.error(result.stderr)
            
    except subprocess.CalledProcessError as e:
        logging.error(f"Script execution failed with return code {e.returncode}")
        logging.error(e.stderr)
        
    except subprocess.TimeoutExpired:
        logging.error("Script execution timed out")
    
    except Exception as e:
        logging.error(f"An error occurred while executing the script: {e}")
