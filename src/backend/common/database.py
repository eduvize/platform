from config import get_database_connection_string
from sqlmodel import create_engine

connection_string = get_database_connection_string()

engine = create_engine(connection_string, echo=True)