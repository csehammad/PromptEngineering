from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User preferences for recommendations
    preferred_genres = Column(String(500))  # comma-separated genres
    preferred_languages = Column(String(100))  # comma-separated language codes
    min_rating = Column(Integer, default=0)  # minimum vote average
    max_runtime = Column(Integer)  # maximum movie length in minutes
    include_adult = Column(Boolean, default=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # API access
    api_key = Column(String(255), unique=True, index=True)
    api_key_expires_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def is_api_key_valid(self) -> bool:
        """
        Check if API key is valid and not expired
        """
        if not self.api_key:
            return False
        if self.api_key_expires_at and datetime.utcnow() > self.api_key_expires_at:
            return False
        return True


class UserRating(Base):
    __tablename__ = "user_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    movie_id = Column(Integer, nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-10 scale
    review = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserRating(user_id={self.user_id}, movie_id={self.movie_id}, rating={self.rating})>" 