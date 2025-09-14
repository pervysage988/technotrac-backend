from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Engine uses DATABASE_URL from settings
engine = create_async_engine(
    settings.database_url,
    future=True,
    echo=settings.debug,  # ✅ only log SQL when debug=True
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """FastAPI dependency for DB session"""
    async with AsyncSessionLocal() as session:
        yield session
