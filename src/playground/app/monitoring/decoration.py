import threading

# Debounce dictionary to keep track of timers for validation
debounce_timers = {}

def debounce(key: str, delay_seconds: int):
    """
    Debounce decorator that accepts a key and delay.
    
    Args:
        key (str): The key to use for the debounce timer
        delay_seconds (int): The delay in seconds before the function is called
    """
    def decorator(func):
        def debounced(*args, **kwargs):
            # Cancel the existing timer if it exists
            if key in debounce_timers and debounce_timers[key]:
                debounce_timers[key].cancel()

            # Create a new timer
            def call_func():
                func(*args, **kwargs)

            # Set a timer to call the function after the delay
            debounce_timers[key] = threading.Timer(delay_seconds, call_func)
            debounce_timers[key].start()

        return debounced
    return decorator
