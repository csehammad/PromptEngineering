from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.security import verify_token
from app.core.cache import increment_rate_limit, get_rate_limit
from app.core.config import settings
from app.models.user import User
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current authenticated user"""
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            return None
        
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            return None
        
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        if user is None or not user.is_active:
            return None
        
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user or raise HTTP exception"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


async def verify_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Verify API key for trusted clients"""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None
    
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_api_key(api_key)
        
        if user and user.is_api_key_valid and user.is_active:
            return user
        
        return None
    except Exception as e:
        logger.error(f"API key verification error: {e}")
        return None


async def rate_limit_middleware(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    api_user: Optional[User] = Depends(verify_api_key)
) -> None:
    """Rate limiting middleware"""
    # Determine user identifier for rate limiting
    if current_user:
        user_id = f"user:{current_user.id}"
    elif api_user:
        user_id = f"api:{api_user.id}"
    else:
        user_id = f"ip:{request.client.host}"
    
    # Check rate limit
    current_count = await increment_rate_limit(user_id, 60)
    
    if current_count > settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {settings.rate_limit_per_minute} requests per minute.",
            headers={"Retry-After": "60"}
        )


async def require_auth(
    current_user: Optional[User] = Depends(get_current_user),
    api_user: Optional[User] = Depends(verify_api_key)
) -> User:
    """Require either JWT token or API key authentication"""
    if current_user:
        return current_user
    elif api_user:
        return api_user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def optional_auth(
    current_user: Optional[User] = Depends(get_current_user),
    api_user: Optional[User] = Depends(verify_api_key)
) -> Optional[User]:
    """Optional authentication - returns user if authenticated, None otherwise"""
    if current_user:
        return current_user
    elif api_user:
        return api_user
    else:
        return None


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Get user service instance"""
    return UserService(db) 