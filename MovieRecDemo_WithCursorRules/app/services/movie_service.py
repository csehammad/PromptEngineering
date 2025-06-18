from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from app.models.movie import Movie
from app.schemas.movie import MovieCreate, MovieUpdate, MovieSearchParams, MovieRecommendation
from app.core.cache import get_cache, set_cache
import logging
import json

logger = logging.getLogger(__name__)


class MovieService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        """Get movie by ID with caching"""
        cache_key = f"movie:{movie_id}"
        cached = await get_cache(cache_key)
        if cached:
            return Movie(**json.loads(cached))
        
        result = await self.db.execute(
            select(Movie).where(Movie.id == movie_id)
        )
        movie = result.scalar_one_or_none()
        
        if movie:
            await set_cache(cache_key, json.dumps(movie.__dict__), expire=3600)
        
        return movie
    
    async def search_movies(self, params: MovieSearchParams) -> List[Movie]:
        """Search movies with filters"""
        query = select(Movie)
        conditions = []
        
        # Text search
        if params.query:
            search_term = f"%{params.query}%"
            conditions.append(
                or_(
                    Movie.title.ilike(search_term),
                    Movie.overview.ilike(search_term),
                    Movie.cast.ilike(search_term),
                    Movie.director.ilike(search_term)
                )
            )
        
        # Genre filter
        if params.genres:
            genre_list = [g.strip() for g in params.genres.split(',')]
            for genre in genre_list:
                conditions.append(Movie.genres.ilike(f"%{genre}%"))
        
        # Rating filter
        if params.min_rating is not None:
            conditions.append(Movie.vote_average >= params.min_rating)
        
        # Runtime filter
        if params.max_runtime is not None:
            conditions.append(Movie.runtime <= params.max_runtime)
        
        # Year filters
        if params.year_from:
            conditions.append(Movie.release_date >= f"{params.year_from}-01-01")
        if params.year_to:
            conditions.append(Movie.release_date <= f"{params.year_to}-12-31")
        
        # Adult content filter
        if not params.include_adult:
            conditions.append(Movie.adult == False)
        
        # Apply conditions
        if conditions:
            query = query.where(and_(*conditions))
        
        # Order by popularity and limit results
        query = query.order_by(desc(Movie.popularity)).offset(params.offset).limit(params.limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_popular_movies(self, limit: int = 20, offset: int = 0) -> List[Movie]:
        """Get most popular movies"""
        cache_key = f"popular_movies:{limit}:{offset}"
        cached = await get_cache(cache_key)
        if cached:
            return [Movie(**json.loads(m)) for m in json.loads(cached)]
        
        result = await self.db.execute(
            select(Movie)
            .where(Movie.adult == False)
            .order_by(desc(Movie.popularity))
            .offset(offset)
            .limit(limit)
        )
        movies = result.scalars().all()
        
        if movies:
            await set_cache(cache_key, json.dumps([m.__dict__ for m in movies]), expire=1800)
        
        return movies
    
    async def get_recommendations_by_genre(self, genre: str, limit: int = 10) -> List[MovieRecommendation]:
        """Get movie recommendations by genre"""
        cache_key = f"genre_recommendations:{genre}:{limit}"
        cached = await get_cache(cache_key)
        if cached:
            return [MovieRecommendation(**r) for r in json.loads(cached)]
        
        result = await self.db.execute(
            select(Movie)
            .where(
                and_(
                    Movie.genres.ilike(f"%{genre}%"),
                    Movie.adult == False,
                    Movie.vote_count >= 100  # Minimum vote count for quality
                )
            )
            .order_by(desc(Movie.popularity))
            .limit(limit)
        )
        movies = result.scalars().all()
        
        recommendations = []
        for movie in movies:
            score = movie.popularity_score
            reason = f"Popular {genre} movie with high ratings"
            recommendations.append(MovieRecommendation(movie=movie, score=score, reason=reason))
        
        if recommendations:
            await set_cache(cache_key, json.dumps([r.dict() for r in recommendations]), expire=3600)
        
        return recommendations
    
    async def get_recommendations_by_director(self, director: str, limit: int = 10) -> List[MovieRecommendation]:
        """Get movie recommendations by director"""
        result = await self.db.execute(
            select(Movie)
            .where(
                and_(
                    Movie.director.ilike(f"%{director}%"),
                    Movie.adult == False
                )
            )
            .order_by(desc(Movie.popularity))
            .limit(limit)
        )
        movies = result.scalars().all()
        
        recommendations = []
        for movie in movies:
            score = movie.popularity_score
            reason = f"Directed by {director}"
            recommendations.append(MovieRecommendation(movie=movie, score=score, reason=reason))
        
        return recommendations
    
    async def get_similar_movies(self, movie_id: int, limit: int = 10) -> List[MovieRecommendation]:
        """Get similar movies based on genre and popularity"""
        movie = await self.get_movie_by_id(movie_id)
        if not movie:
            return []
        
        # Get movies with similar genres
        if movie.genres:
            genre_list = [g.strip() for g in movie.genres.split(',')]
            conditions = []
            for genre in genre_list[:3]:  # Use top 3 genres
                conditions.append(Movie.genres.ilike(f"%{genre}%"))
            
            result = await self.db.execute(
                select(Movie)
                .where(
                    and_(
                        or_(*conditions),
                        Movie.id != movie_id,
                        Movie.adult == False
                    )
                )
                .order_by(desc(Movie.popularity))
                .limit(limit)
            )
            movies = result.scalars().all()
            
            recommendations = []
            for similar_movie in movies:
                score = similar_movie.popularity_score
                reason = f"Similar to '{movie.title}' (same genres)"
                recommendations.append(MovieRecommendation(movie=similar_movie, score=score, reason=reason))
            
            return recommendations
        
        return []
    
    async def get_trending_movies(self, limit: int = 10) -> List[Movie]:
        """Get trending movies (high popularity and recent release)"""
        result = await self.db.execute(
            select(Movie)
            .where(
                and_(
                    Movie.adult == False,
                    Movie.release_date.isnot(None),
                    Movie.popularity > 10  # High popularity threshold
                )
            )
            .order_by(desc(Movie.popularity))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create_movie(self, movie_data: MovieCreate) -> Movie:
        """Create a new movie"""
        movie = Movie(**movie_data.dict())
        self.db.add(movie)
        await self.db.commit()
        await self.db.refresh(movie)
        
        # Clear relevant caches
        await self._clear_movie_caches()
        
        return movie
    
    async def update_movie(self, movie_id: int, movie_data: MovieUpdate) -> Optional[Movie]:
        """Update an existing movie"""
        movie = await self.get_movie_by_id(movie_id)
        if not movie:
            return None
        
        update_data = movie_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(movie, field, value)
        
        await self.db.commit()
        await self.db.refresh(movie)
        
        # Clear relevant caches
        await self._clear_movie_caches()
        
        return movie
    
    async def _clear_movie_caches(self):
        """Clear movie-related caches"""
        cache_patterns = ["popular_movies:", "genre_recommendations:", "movie:"]
        for pattern in cache_patterns:
            # Note: In a real implementation, you'd use Redis SCAN to clear patterns
            # For now, we'll rely on cache expiration
            pass 