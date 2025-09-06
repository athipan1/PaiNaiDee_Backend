from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_async_db
from src.models import User  # Assuming FastAPI can access Flask's models

# Reusable security scheme
token_auth_scheme = HTTPBearer()

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """
    Dependency to get the current user from a JWT token.
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token.credentials,
            settings.jwt_secret_key,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: Subject (sub) claim missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # The identity from flask_jwt_extended is a string, convert to int
        user_id = int(user_id)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (ValueError, TypeError):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In an async context, we need to use the async session to get the user
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_current_user(
    token: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> User | None:
    """
    Dependency to get the current user if a token is provided.
    If no token is provided, returns None.
    """
    if token is None:
        return None

    try:
        # If a token is provided, try to validate it and get the user
        return await get_current_user(token, db)
    except HTTPException:
        # If token is invalid or expired, treat as anonymous user
        return None
