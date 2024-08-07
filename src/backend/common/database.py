from config import get_database_connection_string
from sqlmodel import create_engine
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.inspection import inspect

connection_string = get_database_connection_string()

engine = create_engine(connection_string, echo=True)

def recursive_load_options(model, path):
    """
    Recursively load the specified path and all other relationships on those paths.

    Args:
        model (SQLAlchemy model): The root model to start loading relationships.
        path (str): The dot-separated path string representing the relationships to load.

    Returns:
        list: A list of loader options to be applied to the query.
    """
    # Split the path into individual fields
    fields = path.split('.')
    
    # Start with the first field
    current_field = fields[0]
    remaining_path = '.'.join(fields[1:])

    # Get the relationship for the current field
    current_relationship = getattr(model, current_field)
    
    # Initialize the loader option for the current relationship
    loader_option = selectinload(current_relationship)

    # If there is more path to load, recursively load it
    if remaining_path:
        loader_option = loader_option.options(*recursive_load_options(current_relationship.property.mapper.class_, remaining_path))

    # Recursively load all other relationships on this path
    for related_field in inspect(current_relationship.property.mapper.class_).relationships.keys():
        loader_option = loader_option.options(selectinload(getattr(current_relationship.property.mapper.class_, related_field)))

    return [loader_option]