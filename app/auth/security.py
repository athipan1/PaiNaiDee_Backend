from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_async_db

# Reusable security scheme
token_auth_scheme = HTTPBearer(auto_error=False)


class CurrentUser:
    """Simple user representation for API key authentication"""
    def __init__(self, user_id: str, auth_type: str = "api_key"):
        self.id = user_id
        self.auth_type = auth_type
    
    def __str__(self):
        return f"User(id={self.id}, auth_type={self.auth_type})"


async def verify_api_key(
    x_api_key: Optional[str] = Header(None),
    x_actor_id: Optional[str] = Header(None)
) -> Optional[CurrentUser]:
    """Verify API key authentication"""
    if not x_api_key:
        return None
    
    # Get API keys from settings
    valid_api_keys = getattr(settings, 'api_keys', 'demo-api-key,test-api-key').split(',')
    valid_api_keys = [key.strip() for key in valid_api_keys if key.strip()]
    
    if x_api_key not in valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Use provided actor ID or default
    actor_id = x_actor_id or f"api_user_{x_api_key[:8]}"
    return CurrentUser(actor_id, "api_key")


async def verify_jwt_token(
    token: Optional[HTTPAuthorizationCredentials] = Depends(token_auth_scheme)
) -> Optional[CurrentUser]:
    """Verify JWT token authentication"""
    if not token:
        return None
    
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
        
        return CurrentUser(str(user_id), "jwt")
        
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


async def get_current_user(
    api_user: Optional[CurrentUser] = Depends(verify_api_key),
    jwt_user: Optional[CurrentUser] = Depends(verify_jwt_token)
) -> CurrentUser:
    """
    Dependency to get the current user from either API key or JWT token.
    API key authentication takes precedence over JWT.
    """
    current_user = api_user or jwt_user
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide either X-API-Key header or Authorization Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user


async def get_optional_current_user(
    api_user: Optional[CurrentUser] = Depends(verify_api_key),
    jwt_user: Optional[CurrentUser] = Depends(verify_jwt_token)
) -> Optional[CurrentUser]:
    """
    Dependency to get the current user if authentication is provided.
    Returns None if no authentication is provided.
    """
    return api_user or jwt_user
