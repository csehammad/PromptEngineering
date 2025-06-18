from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import require_auth, optional_auth, rate_limit_middleware
from app.models.user import User
from app.services.movie_service import MovieService
from app.schemas.movie import (
    Movie, MovieCreate, MovieUpdate, MovieSearchParams, 
    MovieRecommendation
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[Movie])
async def get_popular_movies(
    limit: int = Query(20, ge=1, le=100, description="Number of movies to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_middleware)
):
    """Get popular movies (no authentication required)"""
    try:
        movie_service = MovieService(db)
        movies = await movie_service.get_popular_movies(limit=limit, offset=offset)
        return movies
    except Exception as e:
        logger.error(f"Error getting popular movies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/search", response_model=List[Movie])
async def search_movies(
    query: Optional[str] = Query(None, description="Search query"),
    genres: Optional[str] = Query(None, description="Comma-separated genres"),
    min_rating: Optional[float] = Query(None, ge=0, le=10, description="Minimum rating"),
    max_runtime: Optional[int] = Query(None, ge=0, description="Maximum runtime in minutes"),
    year_from: Optional[int] = Query(None, ge=1900, le=2030, description="Release year from"),
    year_to: Optional[int] = Query(None, ge=1900, le=2030, description="Release year to"),
    include_adult: bool = Query(False, description="Include adult content"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_middleware)
):
    """Search movies with filters (no authentication required)"""
    try:
        search_params = MovieSearchParams(
            query=query,
            genres=genres,
            min_rating=min_rating,
            max_runtime=max_runtime,
            year_from=year_from,
            year_to=year_to,
            include_adult=include_adult,
            limit=limit,
            offset=offset
        )
        
        movie_service = MovieService(db)
        movies = await movie_service.search_movies(search_params)
        return movies
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error searching movies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{movie_id}", response_model=Movie)
async def get_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_middleware)
):
    """Get movie by ID (no authentication required)"""
    try:
        movie_service = MovieService(db)
        movie = await movie_service.get_movie_by_id(movie_id)
        
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )
        
        return movie
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting movie {movie_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{movie_id}/similar", response_model=List[MovieRecommendation])
async def get_similar_movies(
    movie_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of similar movies"),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_middleware)
):
    """Get similar movies based on genre and popularity (no authentication required)"""
    try:
        movie_service = MovieService(db)
        recommendations = await movie_service.get_similar_movies(movie_id, limit=limit)
        return recommendations
    except Exception as e:
        logger.error(f"Error getting similar movies for {movie_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/recommendations/genre/{genre}", response_model=List[MovieRecommendation])
async def get_recommendations_by_genre(
    genre: str,
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_middleware)
):
    """Get movie recommendations by genre (no authentication required)"""
    try:
        movie_service = MovieService(db)
        recommendations = await movie_service.get_recommendations_by_genre(genre, limit=limit)
        return recommendations
    except Exception as e:
        logger.error(f"Error getting genre recommendations for {genre}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/recommendations/director/{director}", response_model=List[MovieRecommendation])
async def get_recommendations_by_director(
    director: str,
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_middleware)
):
    """Get movie recommendations by director (no authentication required)"""
    try:
        movie_service = MovieService(db)
        recommendations = await movie_service.get_recommendations_by_director(director, limit=limit)
        return recommendations
    except Exception as e:
        logger.error(f"Error getting director recommendations for {director}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/trending", response_model=List[Movie])
async def get_trending_movies(
    limit: int = Query(10, ge=1, le=50, description="Number of trending movies"),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_middleware)
):
    """Get trending movies (high popularity and recent release) (no authentication required)"""
    try:
        movie_service = MovieService(db)
        movies = await movie_service.get_trending_movies(limit=limit)
        return movies
    except Exception as e:
        logger.error(f"Error getting trending movies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Admin endpoints (require authentication)
@router.post("/", response_model=Movie)
async def create_movie(
    movie_data: MovieCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
    _: None = Depends(rate_limit_middleware)
):
    """Create a new movie (requires authentication)"""
    try:
        movie_service = MovieService(db)
        movie = await movie_service.create_movie(movie_data)
        return movie
    except Exception as e:
        logger.error(f"Error creating movie: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{movie_id}", response_model=Movie)
async def update_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
    _: None = Depends(rate_limit_middleware)
):
    """Update a movie (requires authentication)"""
    try:
        movie_service = MovieService(db)
        movie = await movie_service.update_movie(movie_id, movie_data)
        
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )
        
        return movie
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating movie {movie_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 