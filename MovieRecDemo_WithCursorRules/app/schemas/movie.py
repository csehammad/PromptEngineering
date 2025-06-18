from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class MovieBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    original_title: Optional[str] = Field(None, max_length=255)
    overview: Optional[str] = None
    tagline: Optional[str] = Field(None, max_length=500)
    release_date: Optional[datetime] = None
    runtime: Optional[int] = Field(None, ge=0)
    vote_average: Optional[float] = Field(None, ge=0, le=10)
    vote_count: Optional[int] = Field(None, ge=0)
    popularity: Optional[float] = Field(None, ge=0)
    budget: Optional[int] = Field(None, ge=0)
    revenue: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=50)
    original_language: Optional[str] = Field(None, max_length=10)
    genres: Optional[str] = Field(None, max_length=500)
    production_companies: Optional[str] = Field(None, max_length=1000)
    production_countries: Optional[str] = Field(None, max_length=500)
    director: Optional[str] = Field(None, max_length=255)
    cast: Optional[str] = Field(None, max_length=1000)
    adult: Optional[bool] = False
    video: Optional[bool] = False


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    original_title: Optional[str] = Field(None, max_length=255)
    overview: Optional[str] = None
    tagline: Optional[str] = Field(None, max_length=500)
    release_date: Optional[datetime] = None
    runtime: Optional[int] = Field(None, ge=0)
    vote_average: Optional[float] = Field(None, ge=0, le=10)
    vote_count: Optional[int] = Field(None, ge=0)
    popularity: Optional[float] = Field(None, ge=0)
    budget: Optional[int] = Field(None, ge=0)
    revenue: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=50)
    original_language: Optional[str] = Field(None, max_length=10)
    genres: Optional[str] = Field(None, max_length=500)
    production_companies: Optional[str] = Field(None, max_length=1000)
    production_countries: Optional[str] = Field(None, max_length=500)
    director: Optional[str] = Field(None, max_length=255)
    cast: Optional[str] = Field(None, max_length=1000)
    adult: Optional[bool] = None
    video: Optional[bool] = None


class Movie(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    @property
    def popularity_score(self) -> float:
        """Calculate popularity score for recommendations"""
        base_score = self.popularity or 0.0
        vote_score = (self.vote_average or 0.0) * min((self.vote_count or 0) / 1000, 1.0)
        
        if self.release_date:
            years_old = (datetime.now() - self.release_date).days / 365
            recency_bonus = max(0, 1 - (years_old / 10))
        else:
            recency_bonus = 0.5
        
        financial_bonus = 0
        if self.budget and self.revenue and self.budget > 0:
            roi = (self.revenue - self.budget) / self.budget
            financial_bonus = min(roi / 10, 1.0)
        
        return base_score + vote_score + (recency_bonus * 0.5) + (financial_bonus * 0.3)
    
    class Config:
        from_attributes = True


class MovieRecommendation(BaseModel):
    movie: Movie
    score: float = Field(..., description="Recommendation score")
    reason: str = Field(..., description="Reason for recommendation")


class MovieSearchParams(BaseModel):
    query: Optional[str] = Field(None, description="Search query")
    genres: Optional[str] = Field(None, description="Comma-separated genres")
    min_rating: Optional[float] = Field(None, ge=0, le=10, description="Minimum vote average")
    max_runtime: Optional[int] = Field(None, ge=0, description="Maximum runtime in minutes")
    year_from: Optional[int] = Field(None, ge=1900, le=2030, description="Release year from")
    year_to: Optional[int] = Field(None, ge=1900, le=2030, description="Release year to")
    include_adult: Optional[bool] = Field(False, description="Include adult content")
    limit: Optional[int] = Field(20, ge=1, le=100, description="Number of results")
    offset: Optional[int] = Field(0, ge=0, description="Pagination offset")
    
    @validator('year_to')
    def validate_year_range(cls, v, values):
        if v and 'year_from' in values and values['year_from']:
            if v < values['year_from']:
                raise ValueError('year_to must be greater than or equal to year_from')
        return v 