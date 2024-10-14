import functools
import inspect
from fastapi import Depends, Request
from fastapi.dependencies.utils import get_dependant, solve_dependencies
from contextlib import AsyncExitStack
from typing import Callable
from app.main import app  # Ensure you have access to your FastAPI app instance

def inject_dependencies():
    def decorator(method: Callable):
        @functools.wraps(method)
        async def wrapper(self, *args, **kwargs):
            # Create a dummy request scope
            scope = {
                "type": "http",
                "method": "GET",
                "path": "/",
                "headers": [],
                "query_string": b"",
                "client": ("127.0.0.1", 0),
                "server": ("127.0.0.1", 8000),
                "app": app,
            }
            request = Request(scope=scope)

            # Get the unbound method (original function)
            func = method.__func__ if hasattr(method, '__func__') else method

            # Create a dependant for the method
            dependant = get_dependant(path="", call=func)

            # Remove 'self', 'sid', and 'data' from parameters
            ignore_params = {'self', 'sid', 'data', 'environ'}
            dependant.query_params = [param for param in dependant.query_params if param.name not in ignore_params]
            dependant.path_params = [param for param in dependant.path_params if param.name not in ignore_params]
            dependant.header_params = [param for param in dependant.header_params if param.name not in ignore_params]
            dependant.cookie_params = [param for param in dependant.cookie_params if param.name not in ignore_params]
            dependant.body_params = [param for param in dependant.body_params if param.name not in ignore_params]
            dependant.dependencies = [dep for dep in dependant.dependencies if dep.name not in ignore_params]

            # Solve dependencies
            async with AsyncExitStack() as async_exit_stack:
                solved_result = await solve_dependencies(
                    request=request,
                    dependant=dependant,
                    dependency_overrides_provider=app,
                    async_exit_stack=async_exit_stack,
                )
                values, errors, *_ = solved_result

                if errors:
                    raise Exception(errors)

                # Map args to parameter names
                sig = inspect.signature(func)
                bound_args = sig.bind_partial(self, *args, **kwargs)
                bound_args.apply_defaults()

                # Update with resolved dependencies
                for k, v in values.items():
                    bound_args.arguments[k] = v

                # Call the method with all arguments
                return await method(**bound_args.arguments)
        return wrapper
    return decorator