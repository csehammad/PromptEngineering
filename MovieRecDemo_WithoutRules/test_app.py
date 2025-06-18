import requests
import json

# Base URL for the microservice
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_get_all_movies():
    """Test getting all movies"""
    print("Testing get all movies...")
    response = requests.get(f"{BASE_URL}/movies")
    print(f"Status: {response.status_code}")
    print(f"Total movies: {len(response.json())}")
    print(f"First movie: {response.json()[0]['title']}")
    print()

def test_get_movie_by_id():
    """Test getting a specific movie by ID"""
    print("Testing get movie by ID...")
    response = requests.get(f"{BASE_URL}/movies/1")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        movie = response.json()
        print(f"Movie: {movie['title']} ({movie['year']})")
    print()

def test_get_movies_by_genre():
    """Test getting movies by genre"""
    print("Testing get movies by genre...")
    response = requests.get(f"{BASE_URL}/movies/genre/Drama")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        movies = response.json()
        print(f"Found {len(movies)} Drama movies")
        for movie in movies[:3]:  # Show first 3
            print(f"- {movie['title']}")
    print()

def test_get_recommendations():
    """Test getting personalized recommendations"""
    print("Testing get recommendations...")
    payload = {
        "user_id": "test_user",
        "preferred_genres": ["Action", "Sci-Fi"],
        "min_rating": 8.5,
        "min_year": 2000,
        "limit": 3
    }
    response = requests.post(f"{BASE_URL}/recommendations", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"User ID: {result['user_id']}")
        print(f"Total recommendations: {result['total_recommendations']}")
        for movie in result['recommendations']:
            print(f"- {movie['title']} ({movie['rating']})")
    print()

def test_get_random_recommendations():
    """Test getting random recommendations"""
    print("Testing get random recommendations...")
    response = requests.get(f"{BASE_URL}/recommendations/random?limit=3")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Total recommendations: {result['total_recommendations']}")
        for movie in result['recommendations']:
            print(f"- {movie['title']} ({movie['rating']})")
    print()

def main():
    """Run all tests"""
    print("🎬 Movie Recommendation Microservice Tests")
    print("=" * 50)
    
    try:
        test_health_check()
        test_get_all_movies()
        test_get_movie_by_id()
        test_get_movies_by_genre()
        test_get_recommendations()
        test_get_random_recommendations()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the microservice.")
        print("Make sure the service is running on http://localhost:8000")
        print("Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 