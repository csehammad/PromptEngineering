from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime


class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    original_title = Column(String(255))
    overview = Column(Text)
    tagline = Column(String(500))
    
    # Release and runtime
    release_date = Column(DateTime)
    runtime = Column(Integer)  # in minutes
    
    # Ratings and popularity
    vote_average = Column(Float, default=0.0)
    vote_count = Column(Integer, default=0)
    popularity = Column(Float, default=0.0)
    
    # Financial data
    budget = Column(Integer, default=0)
    revenue = Column(Integer, default=0)
    
    # Status and language
    status = Column(String(50))  # Released, Post Production, etc.
    original_language = Column(String(10))
    
    # Genres (stored as comma-separated string for simplicity)
    genres = Column(String(500))
    
    # Production details
    production_companies = Column(String(1000))
    production_countries = Column(String(500))
    
    # Cast and crew (simplified for popularity-based recommendations)
    director = Column(String(255))
    cast = Column(String(1000))  # Main cast as comma-separated
    
    # Technical details
    adult = Column(Boolean, default=False)
    video = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_movies_popularity', 'popularity'),
        Index('idx_movies_vote_average', 'vote_average'),
        Index('idx_movies_release_date', 'release_date'),
        Index('idx_movies_genres', 'genres'),
    )
    
    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}', popularity={self.popularity})>"
    
    @property
    def popularity_score(self) -> float:
        """
        Calculate popularity score based on multiple factors
        """
        # Base popularity from TMDB
        base_score = self.popularity or 0.0
        
        # Adjust based on vote average and count
        vote_score = (self.vote_average or 0.0) * min((self.vote_count or 0) / 1000, 1.0)
        
        # Recency bonus (newer movies get slight boost)
        if self.release_date:
            years_old = (datetime.now() - self.release_date).days / 365
            recency_bonus = max(0, 1 - (years_old / 10))  # Decay over 10 years
        else:
            recency_bonus = 0.5
        
        # Financial success bonus
        financial_bonus = 0
        if self.budget and self.revenue and self.budget > 0:
            roi = (self.revenue - self.budget) / self.budget
            financial_bonus = min(roi / 10, 1.0)  # Cap at 1.0
        
        return base_score + vote_score + (recency_bonus * 0.5) + (financial_bonus * 0.3) 