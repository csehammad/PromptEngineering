from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from datetime import datetime, timedelta
from app.models.user import User, UserRating
from app.schemas.user import UserCreate, UserUpdate, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token, generate_api_key
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """Get user by API key"""
        result = await self.db.execute(
            select(User).where(User.api_key == api_key)
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if username or email already exists
        existing_user = await self.get_user_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already registered")
        
        existing_email = await self.get_user_by_email(user_data.email)
        if existing_email:
            raise ValueError("Email already registered")
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            preferred_genres=user_data.preferred_genres,
            preferred_languages=user_data.preferred_languages,
            min_rating=user_data.min_rating,
            max_runtime=user_data.max_runtime,
            include_adult=user_data.include_adult
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        return user
    
    async def create_access_token_for_user(self, user: User) -> str:
        """Create access token for user"""
        data = {
            "sub": user.username,
            "user_id": user.id
        }
        return create_access_token(data)
    
    async def generate_api_key_for_user(self, user: User) -> str:
        """Generate new API key for user"""
        api_key = generate_api_key()
        user.api_key = api_key
        user.api_key_expires_at = datetime.utcnow() + timedelta(days=365)  # 1 year expiration
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return api_key
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        
        # Check for unique constraints
        if "username" in update_data:
            existing = await self.get_user_by_username(update_data["username"])
            if existing and existing.id != user_id:
                raise ValueError("Username already taken")
        
        if "email" in update_data:
            existing = await self.get_user_by_email(update_data["email"])
            if existing and existing.id != user_id:
                raise ValueError("Email already taken")
        
        # Update fields
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def add_user_rating(self, user_id: int, movie_id: int, rating: int, review: Optional[str] = None) -> UserRating:
        """Add or update user rating for a movie"""
        # Check if rating already exists
        result = await self.db.execute(
            select(UserRating).where(
                and_(UserRating.user_id == user_id, UserRating.movie_id == movie_id)
            )
        )
        existing_rating = result.scalar_one_or_none()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating
            if review is not None:
                existing_rating.review = review
            existing_rating.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing_rating)
            return existing_rating
        else:
            # Create new rating
            user_rating = UserRating(
                user_id=user_id,
                movie_id=movie_id,
                rating=rating,
                review=review
            )
            self.db.add(user_rating)
            await self.db.commit()
            await self.db.refresh(user_rating)
            return user_rating
    
    async def get_user_ratings(self, user_id: int, limit: int = 20, offset: int = 0) -> list[UserRating]:
        """Get user's movie ratings"""
        result = await self.db.execute(
            select(UserRating)
            .where(UserRating.user_id == user_id)
            .order_by(UserRating.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def delete_user_rating(self, user_id: int, movie_id: int) -> bool:
        """Delete user rating for a movie"""
        result = await self.db.execute(
            select(UserRating).where(
                and_(UserRating.user_id == user_id, UserRating.movie_id == movie_id)
            )
        )
        rating = result.scalar_one_or_none()
        
        if rating:
            await self.db.delete(rating)
            await self.db.commit()
            return True
        
        return False 