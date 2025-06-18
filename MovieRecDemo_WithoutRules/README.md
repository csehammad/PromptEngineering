# Movie Recommendation Microservice

A FastAPI-based microservice that provides movie recommendations based on user preferences. This service includes a sample movie database and various recommendation algorithms.

## Features

- 🎬 Movie recommendations based on genres, ratings, and years
- 🔍 Search movies by ID or genre
- 📊 Health check endpoint
- 🎯 Random recommendation generator
- 📚 Interactive API documentation (Swagger UI)
- 🚀 Fast and lightweight FastAPI implementation

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Service

Start the microservice:
```bash
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at `http://localhost:8000`

## API Documentation

Once the service is running, you can access:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Root Endpoint
- `GET /` - Service information and available endpoints

### Health Check
- `GET /health` - Service health status

### Movies
- `GET /movies` - Get all available movies
- `GET /movies/{movie_id}` - Get a specific movie by ID
- `GET /movies/genre/{genre}` - Get movies by specific genre

### Recommendations
- `POST /recommendations` - Get personalized movie recommendations
- `GET /recommendations/random` - Get random movie recommendations

## Usage Examples

### Get All Movies
```bash
curl http://localhost:8000/movies
```

### Get Movie by ID
```bash
curl http://localhost:8000/movies/1
```

### Get Movies by Genre
```bash
curl http://localhost:8000/movies/genre/Drama
```

### Get Personalized Recommendations
```bash
curl -X POST "http://localhost:8000/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "preferred_genres": ["Action", "Sci-Fi"],
    "min_rating": 8.5,
    "min_year": 2000,
    "limit": 3
  }'
```

### Get Random Recommendations
```bash
curl "http://localhost:8000/recommendations/random?limit=5"
```

## Request/Response Models

### Recommendation Request
```json
{
  "user_id": "string (optional)",
  "preferred_genres": ["string"] (optional),
  "min_rating": 0.0 (optional),
  "max_year": 2024 (optional),
  "min_year": 1900 (optional),
  "limit": 5 (optional)
}
```

### Movie Object
```json
{
  "id": 1,
  "title": "Movie Title",
  "genre": ["Genre1", "Genre2"],
  "rating": 8.5,
  "year": 2020,
  "director": "Director Name",
  "description": "Movie description"
}
```

### Recommendation Response
```json
{
  "user_id": "user123",
  "recommendations": [Movie],
  "timestamp": "2024-01-01T12:00:00",
  "total_recommendations": 5
}
```

## Sample Movie Database

The service includes a curated list of popular movies with the following information:
- Movie ID and title
- Genres (multiple genres per movie)
- IMDb-style ratings
- Release year
- Director
- Brief description

## Development

### Project Structure
```
MicroservicesDemo/
├── app.py              # Main FastAPI application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Adding More Movies

To add more movies to the database, edit the `MOVIES_DATABASE` list in `app.py`:

```python
{
    "id": 11,
    "title": "Your Movie Title",
    "genre": ["Genre1", "Genre2"],
    "rating": 8.0,
    "year": 2023,
    "director": "Director Name",
    "description": "Movie description"
}
```

### Extending the Service

You can easily extend this service by:
- Adding more sophisticated recommendation algorithms
- Integrating with external movie databases (TMDB, OMDB)
- Adding user authentication and personalization
- Implementing caching for better performance
- Adding database persistence (PostgreSQL, MongoDB)

## Docker Support

To run with Docker:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t movie-recommendation .
docker run -p 8000:8000 movie-recommendation
```

## License

This project is open source and available under the MIT License. 