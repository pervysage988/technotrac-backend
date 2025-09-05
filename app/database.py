from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create the async engine for PostgreSQL
engine = create_async_engine(settings.database_url, echo=True)

# Create a session factory bound to the engine
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency to get DB session in routes
async def get_db():
    async with async_session() as session:
        yield session
