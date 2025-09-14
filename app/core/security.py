# app/core/security.py
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.db.models.user import User, UserRole

# OAuth2 token URL (matches auth router)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/otp/verify")


# -------------------------------
# JWT utils
# -------------------------------
def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    """Generate a JWT token with given data payload."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_delta or settings.access_token_exp_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.primary_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def _decode_with_rotation(token: str) -> dict:
    """Try decoding against all configured secrets (for key rotation)."""
    last_err: Exception | None = None
    for key in settings.all_secret_keys:
        try:
            return jwt.decode(token, key, algorithms=[settings.jwt_algorithm])
        except JWTError as e:
            last_err = e
            continue
    raise HTTPException(status_code=401, detail="Invalid or expired token") from last_err


# -------------------------------
# User dependencies
# -------------------------------
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Decode JWT and load the User from DB."""
    payload = _decode_with_rotation(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.id == user_id))
        user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(*allowed_roles: UserRole):
    """Factory: ensure the user has one of the allowed roles."""
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if allowed_roles and user.role not in allowed_roles:
            allowed_str = ", ".join(r.value for r in allowed_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Only {allowed_str} allowed",
            )
        return user
    return role_checker


# Convenience
require_owner = require_role(UserRole.OWNER)
require_farmer = require_role(UserRole.FARMER)
require_admin = require_role(UserRole.ADMIN)
