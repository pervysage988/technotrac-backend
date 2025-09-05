# app/core/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# ✅ Use asyncpg driver in DATABASE_URL
# Example:
# postgresql+asyncpg://user:password@host:port/dbname

engine = create_async_engine(
    settings.database_url,
    echo=True,            # Log SQL queries (turn off in production)
    future=True
)

# Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
