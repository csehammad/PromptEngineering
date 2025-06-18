# Movie Recommendation Microservice

A production-ready, scalable movie recommendation microservice built with FastAPI, featuring popularity-based recommendations, user authentication, rate limiting, and comprehensive security measures.

## 🚀 Features

- **Popularity-based Movie Recommendations**: Advanced scoring algorithm considering popularity, ratings, recency, and financial success
- **Comprehensive Movie Data**: Full movie attributes including genres, cast, director, ratings, financial data, and more
- **Dual Authentication**: JWT tokens for web clients and API keys for trusted applications
- **Rate Limiting**: Configurable rate limiting per user/IP with Redis
- **Caching**: Redis-based caching for improved performance
- **Security-by-Design**: Comprehensive security measures including input validation, CORS, and secure defaults
- **Scalable Architecture**: Clean architecture with proper separation of concerns
- **Docker Support**: Complete containerization with Docker and Docker Compose
- **Supabase Integration**: PostgreSQL database with Supabase
- **API Documentation**: Automatic OpenAPI documentation with Swagger UI

## 🏗️ Architecture

### Technology Stack
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL (Supabase)
- **Cache**: Redis 7
- **Authentication**: JWT + API Keys
- **Validation**: Pydantic
- **ORM**: SQLAlchemy 2.0 (async)
- **Containerization**: Docker & Docker Compose

### Project Structure
```
app/
├── api/v1/endpoints/     # API endpoints
├── core/                 # Configuration, security, database
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── services/            # Business logic
└── main.py             # FastAPI application
```

## 🔧 Setup & Installation

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Supabase account

### 1. Clone and Setup
```bash
git clone <repository-url>
cd MicroserviceDemo_WithCursorRules
```

### 2. Environment Configuration
Copy the example environment file and configure your settings:
```bash
cp env.example .env
```

Edit `.env` with your configuration:
```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/movierecs
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Security Configuration
SECRET_KEY=your-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your-redis-password

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### 3. Docker Deployment
```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d
```

### 4. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/api-key` - Generate API key for trusted clients
- `GET /api/v1/auth/me` - Get current user info

#### Movies (Public)
- `GET /api/v1/movies/` - Get popular movies
- `GET /api/v1/movies/search` - Search movies with filters
- `GET /api/v1/movies/{movie_id}` - Get movie by ID
- `GET /api/v1/movies/{movie_id}/similar` - Get similar movies
- `GET /api/v1/movies/recommendations/genre/{genre}` - Get recommendations by genre
- `GET /api/v1/movies/recommendations/director/{director}` - Get recommendations by director
- `GET /api/v1/movies/trending` - Get trending movies

#### Movies (Authenticated)
- `POST /api/v1/movies/` - Create new movie
- `PUT /api/v1/movies/{movie_id}` - Update movie

## 🔐 Security Features

### Authentication Methods
1. **JWT Tokens**: For web applications and user sessions
2. **API Keys**: For trusted client applications (1-year expiration)

### Security Measures
- **Input Validation**: Comprehensive Pydantic validation
- **Rate Limiting**: Per-user/IP rate limiting with Redis
- **CORS Protection**: Configurable CORS policies
- **Secure Headers**: Trusted host middleware
- **Password Hashing**: bcrypt with secure defaults
- **Token Security**: JWT with configurable expiration
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Error Handling**: Secure error messages without information leakage

### Rate Limiting
- Default: 60 requests per minute per user/IP
- Configurable via `RATE_LIMIT_PER_MINUTE` environment variable
- Redis-based with automatic expiration

## 🎯 Recommendation Algorithm

The popularity-based recommendation system considers multiple factors:

1. **Base Popularity**: TMDB popularity score
2. **Vote Score**: Weighted by vote count and average
3. **Recency Bonus**: Newer movies get a slight boost
4. **Financial Success**: ROI-based bonus for successful movies

### Scoring Formula
```
Popularity Score = Base Popularity + Vote Score + (Recency Bonus × 0.5) + (Financial Bonus × 0.3)
```

## 🐳 Docker Configuration

### Production Dockerfile
- Multi-stage build for optimization
- Non-root user for security
- Health checks included
- Minimal attack surface

### Docker Compose
- FastAPI application
- Redis for caching and rate limiting
- Volume persistence for Redis data
- Health checks and restart policies

## 📊 Monitoring & Logging

### Logging
- Structured logging with configurable levels
- Request/response logging with timing
- Error tracking with stack traces
- Security event logging

### Health Checks
- `/health` endpoint for monitoring
- Database connectivity checks
- Redis connectivity checks
- Docker health checks

## 🔄 Database Schema

### Movies Table
- Comprehensive movie attributes
- Indexed for performance
- Popularity scoring
- Genre and metadata support

### Users Table
- Secure authentication
- User preferences for recommendations
- API key management
- Account status tracking

### User Ratings Table
- User movie ratings (1-10 scale)
- Review support
- Timestamp tracking

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Secure configuration management
2. **Database**: Use managed PostgreSQL service
3. **Redis**: Use managed Redis service
4. **Load Balancer**: Configure for horizontal scaling
5. **Monitoring**: Implement APM and logging
6. **SSL/TLS**: Configure HTTPS termination
7. **Backup**: Regular database backups

### Scaling
- Stateless design for horizontal scaling
- Redis clustering for high availability
- Database connection pooling
- Caching strategies for performance

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### Test Categories
- Unit tests for business logic
- Integration tests for database operations
- Security tests for authentication
- API tests for endpoints

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SUPABASE_URL` | Supabase project URL | Required |
| `SUPABASE_KEY` | Supabase API key | Required |
| `SECRET_KEY` | JWT secret key | Auto-generated |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per user | `60` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the logs for error details
- Ensure all environment variables are configured
- Verify database and Redis connectivity 