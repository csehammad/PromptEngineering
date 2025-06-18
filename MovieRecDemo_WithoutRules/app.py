from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random
import json
from datetime import datetime

app = FastAPI(
    title="Movie Recommendation Microservice",
    description="A microservice that provides movie recommendations based on user preferences",
    version="1.0.0"
)

# Sample movie database
MOVIES_DATABASE = [
    {
        "id": 1,
        "title": "The Shawshank Redemption",
        "genre": ["Drama"],
        "rating": 9.3,
        "year": 1994,
        "director": "Frank Darabont",
        "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency."
    },
    {
        "id": 2,
        "title": "The Godfather",
        "genre": ["Crime", "Drama"],
        "rating": 9.2,
        "year": 1972,
        "director": "Francis Ford Coppola",
        "description": "The aging patriarch of an organized crime dynasty transfers control to his reluctant son."
    },
    {
        "id": 3,
        "title": "Pulp Fiction",
        "genre": ["Crime", "Drama"],
        "rating": 8.9,
        "year": 1994,
        "director": "Quentin Tarantino",
        "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine."
    },
    {
        "id": 4,
        "title": "The Dark Knight",
        "genre": ["Action", "Crime", "Drama"],
        "rating": 9.0,
        "year": 2008,
        "director": "Christopher Nolan",
        "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham."
    },
    {
        "id": 5,
        "title": "Fight Club",
        "genre": ["Drama"],
        "rating": 8.8,
        "year": 1999,
        "director": "David Fincher",
        "description": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club."
    },
    {
        "id": 6,
        "title": "Inception",
        "genre": ["Action", "Adventure", "Sci-Fi"],
        "rating": 8.8,
        "year": 2010,
        "director": "Christopher Nolan",
        "description": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task."
    },
    {
        "id": 7,
        "title": "The Matrix",
        "genre": ["Action", "Sci-Fi"],
        "rating": 8.7,
        "year": 1999,
        "director": "Lana Wachowski",
        "description": "A computer programmer discovers that reality as he knows it is a simulation created by machines."
    },
    {
        "id": 8,
        "title": "Goodfellas",
        "genre": ["Biography", "Crime", "Drama"],
        "rating": 8.7,
        "year": 1990,
        "director": "Martin Scorsese",
        "description": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen."
    },
    {
        "id": 9,
        "title": "The Silence of the Lambs",
        "genre": ["Crime", "Drama", "Thriller"],
        "rating": 8.6,
        "year": 1991,
        "director": "Jonathan Demme",
        "description": "A young FBI cadet must receive the help of an incarcerated and manipulative cannibal killer."
    },
    {
        "id": 10,
        "title": "Interstellar",
        "genre": ["Adventure", "Drama", "Sci-Fi"],
        "rating": 8.6,
        "year": 2014,
        "director": "Christopher Nolan",
        "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival."
    }
]

# Pydantic models
class Movie(BaseModel):
    id: int
    title: str
    genre: List[str]
    rating: float
    year: int
    director: str
    description: str

class RecommendationRequest(BaseModel):
    user_id: Optional[str] = None
    preferred_genres: Optional[List[str]] = None
    min_rating: Optional[float] = 0.0
    max_year: Optional[int] = None
    min_year: Optional[int] = None
    limit: Optional[int] = 5

class RecommendationResponse(BaseModel):
    user_id: Optional[str]
    recommendations: List[Movie]
    timestamp: str
    total_recommendations: int

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with service information"""
    return {
        "message": "Movie Recommendation Microservice",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "movies": "/movies",
            "recommendations": "/recommendations",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        service="movie-recommendation"
    )

@app.get("/movies", response_model=List[Movie])
async def get_all_movies():
    """Get all available movies"""
    return MOVIES_DATABASE

@app.get("/movies/{movie_id}", response_model=Movie)
async def get_movie(movie_id: int):
    """Get a specific movie by ID"""
    for movie in MOVIES_DATABASE:
        if movie["id"] == movie_id:
            return movie
    raise HTTPException(status_code=404, detail="Movie not found")

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get movie recommendations based on user preferences"""
    
    # Start with all movies
    candidates = MOVIES_DATABASE.copy()
    
    # Filter by minimum rating
    if request.min_rating:
        candidates = [movie for movie in candidates if movie["rating"] >= request.min_rating]
    
    # Filter by year range
    if request.min_year:
        candidates = [movie for movie in candidates if movie["year"] >= request.min_year]
    
    if request.max_year:
        candidates = [movie for movie in candidates if movie["year"] <= request.max_year]
    
    # Filter by preferred genres if provided
    if request.preferred_genres:
        genre_filtered = []
        for movie in candidates:
            if any(genre.lower() in [g.lower() for g in movie["genre"]] for genre in request.preferred_genres):
                genre_filtered.append(movie)
        candidates = genre_filtered
    
    # Sort by rating (highest first)
    candidates.sort(key=lambda x: x["rating"], reverse=True)
    
    # Apply limit
    limit = request.limit or 5
    recommendations = candidates[:limit]
    
    # If no recommendations found, return random movies
    if not recommendations:
        recommendations = random.sample(MOVIES_DATABASE, min(limit, len(MOVIES_DATABASE)))
    
    return RecommendationResponse(
        user_id=request.user_id,
        recommendations=recommendations,
        timestamp=datetime.now().isoformat(),
        total_recommendations=len(recommendations)
    )

@app.get("/recommendations/random", response_model=RecommendationResponse)
async def get_random_recommendations(limit: int = 5):
    """Get random movie recommendations"""
    if limit > len(MOVIES_DATABASE):
        limit = len(MOVIES_DATABASE)
    
    recommendations = random.sample(MOVIES_DATABASE, limit)
    
    return RecommendationResponse(
        user_id=None,
        recommendations=recommendations,
        timestamp=datetime.now().isoformat(),
        total_recommendations=len(recommendations)
    )

@app.get("/movies/genre/{genre}", response_model=List[Movie])
async def get_movies_by_genre(genre: str):
    """Get movies by specific genre"""
    genre_lower = genre.lower()
    movies = [
        movie for movie in MOVIES_DATABASE 
        if any(g.lower() == genre_lower for g in movie["genre"])
    ]
    
    if not movies:
        raise HTTPException(status_code=404, detail=f"No movies found for genre: {genre}")
    
    return movies

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 