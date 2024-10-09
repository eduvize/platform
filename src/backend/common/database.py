from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator

from config import get_database_connection_string

# Get the database connection string
connection_string = get_database_connection_string()

# Ensure the connection string is async
if not connection_string.startswith('postgresql+asyncpg://'):
    async_connection_string = connection_string.replace('postgresql://', 'postgresql+asyncpg://')
else:
    async_connection_string = connection_string

# Create an async engine
async_engine = create_async_engine(
    async_connection_string,
    echo=True,
    future=True
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates and yields an async database session.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session.
    """
    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session