import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.movie_service import MovieService
from app.schemas.movie import MovieSearchParams
from app.models.movie import Movie


@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def movie_service(mock_db):
    """Movie service with mocked database"""
    return MovieService(mock_db)


@pytest.fixture
def sample_movie():
    """Sample movie data"""
    return Movie(
        id=1,
        title="Test Movie",
        overview="A test movie",
        popularity=100.0,
        vote_average=8.5,
        vote_count=1000,
        genres="Action,Adventure",
        director="Test Director",
        cast="Actor 1,Actor 2"
    )


class TestMovieService:
    """Test cases for MovieService"""
    
    @pytest.mark.asyncio
    async def test_get_movie_by_id_success(self, movie_service, mock_db, sample_movie):
        """Test successful movie retrieval by ID"""
        # Mock database response
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_movie
        mock_db.execute.return_value = mock_result
        
        # Test
        result = await movie_service.get_movie_by_id(1)
        
        # Assertions
        assert result is not None
        assert result.id == 1
        assert result.title == "Test Movie"
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_movie_by_id_not_found(self, movie_service, mock_db):
        """Test movie retrieval when movie doesn't exist"""
        # Mock database response
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Test
        result = await movie_service.get_movie_by_id(999)
        
        # Assertions
        assert result is None
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_movies_with_query(self, movie_service, mock_db, sample_movie):
        """Test movie search with query parameter"""
        # Mock database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_movie]
        mock_db.execute.return_value = mock_result
        
        # Test
        search_params = MovieSearchParams(query="test", limit=10, offset=0)
        result = await movie_service.search_movies(search_params)
        
        # Assertions
        assert len(result) == 1
        assert result[0].title == "Test Movie"
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_popular_movies(self, movie_service, mock_db, sample_movie):
        """Test getting popular movies"""
        # Mock database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_movie]
        mock_db.execute.return_value = mock_result
        
        # Test
        result = await movie_service.get_popular_movies(limit=10, offset=0)
        
        # Assertions
        assert len(result) == 1
        assert result[0].title == "Test Movie"
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_recommendations_by_genre(self, movie_service, mock_db, sample_movie):
        """Test getting recommendations by genre"""
        # Mock database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_movie]
        mock_db.execute.return_value = mock_result
        
        # Test
        result = await movie_service.get_recommendations_by_genre("Action", limit=10)
        
        # Assertions
        assert len(result) == 1
        assert result[0].movie.title == "Test Movie"
        assert result[0].reason == "Popular Action movie with high ratings"
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_similar_movies(self, movie_service, mock_db, sample_movie):
        """Test getting similar movies"""
        # Mock get_movie_by_id to return a movie with genres
        movie_service.get_movie_by_id = AsyncMock(return_value=sample_movie)
        
        # Mock database response for similar movies
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_movie]
        mock_db.execute.return_value = mock_result
        
        # Test
        result = await movie_service.get_similar_movies(1, limit=10)
        
        # Assertions
        assert len(result) == 1
        assert result[0].movie.title == "Test Movie"
        assert "same genres" in result[0].reason
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_similar_movies_no_movie_found(self, movie_service, mock_db):
        """Test getting similar movies when original movie doesn't exist"""
        # Mock get_movie_by_id to return None
        movie_service.get_movie_by_id = AsyncMock(return_value=None)
        
        # Test
        result = await movie_service.get_similar_movies(999, limit=10)
        
        # Assertions
        assert result == []
        mock_db.execute.assert_not_called()
    
    def test_movie_popularity_score(self, sample_movie):
        """Test movie popularity score calculation"""
        # Test popularity score calculation
        score = sample_movie.popularity_score
        
        # Assertions
        assert score > 0
        assert isinstance(score, float)
        # Base popularity should be included
        assert score >= sample_movie.popularity 