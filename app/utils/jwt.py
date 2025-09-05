# app/utils/jwt.py
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from jose import jwt, JWTError   # use python-jose for consistency
from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.core.config import settings

# JWT config
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_exp_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/otp/verify")


def create_jwt_token(data: dict, expires_delta: timedelta | None = None):
    """Create a JWT access token using the newest key"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.primary_secret_key,   # ✅ always use newest key
        algorithm=ALGORITHM,
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Decode JWT against all keys and return the user"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    for key in settings.all_secret_keys:   # ✅ try all keys for rotation
        try:
            payload = jwt.decode(token, key, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if not user_id:
                raise credentials_exception
            break
        except JWTError:
            continue
    else:
        raise credentials_exception

    # Load user from DB
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise credentials_exception

    return user


def require_role(*roles: str):
    """Dependency to enforce role-based access control."""
    async def role_guard(user=Depends(get_current_user)):
        if user.role.value not in roles:  # compare DB role with allowed roles
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return role_guard
