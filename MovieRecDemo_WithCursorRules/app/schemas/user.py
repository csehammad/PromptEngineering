from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    preferred_genres: Optional[str] = Field(None, max_length=500)
    preferred_languages: Optional[str] = Field(None, max_length=100)
    min_rating: Optional[int] = Field(0, ge=0, le=10)
    max_runtime: Optional[int] = Field(None, ge=0)
    include_adult: Optional[bool] = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    preferred_genres: Optional[str] = Field(None, max_length=500)
    preferred_languages: Optional[str] = Field(None, max_length=100)
    min_rating: Optional[int] = Field(None, ge=0, le=10)
    max_runtime: Optional[int] = Field(None, ge=0)
    include_adult: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    api_key: Optional[str] = None
    api_key_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    username: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None


class UserRatingCreate(BaseModel):
    movie_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=10)
    review: Optional[str] = None


class UserRatingUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=10)
    review: Optional[str] = None


class UserRating(UserRatingCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyResponse(BaseModel):
    api_key: str
    expires_at: datetime
    message: str = "API key generated successfully" 