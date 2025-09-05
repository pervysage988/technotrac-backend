# app/core/deps.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session

# Common dependency to inject DB session into routes
async def get_db(session: AsyncSession = Depends(get_session)) -> AsyncSession:
    return session
 
