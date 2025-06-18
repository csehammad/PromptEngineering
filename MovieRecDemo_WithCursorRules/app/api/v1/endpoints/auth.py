from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import require_auth, rate_limit_middleware
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserLogin, Token, User, APIKeyResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=User)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_middleware)
):
    """Register a new user"""
    try:
        user_service = UserService(db)
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_middleware)
):
    """Login user and get access token"""
    try:
        user_service = UserService(db)
        user = await user_service.authenticate_user(
            user_credentials.username, 
            user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = await user_service.create_access_token_for_user(user)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutes
            user_id=user.id,
            username=user.username
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/api-key", response_model=APIKeyResponse)
async def generate_api_key(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
    _: None = Depends(rate_limit_middleware)
):
    """Generate API key for trusted client access"""
    try:
        user_service = UserService(db)
        api_key = await user_service.generate_api_key_for_user(current_user)
        
        return APIKeyResponse(
            api_key=api_key,
            expires_at=current_user.api_key_expires_at
        )
    except Exception as e:
        logger.error(f"Error generating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(require_auth),
    _: None = Depends(rate_limit_middleware)
):
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout_user(
    _: None = Depends(rate_limit_middleware)
):
    """Logout user (client should discard token)"""
    return {"message": "Successfully logged out"} 