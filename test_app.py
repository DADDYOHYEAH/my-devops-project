"""
DevOps Flix - Test Suite
pytest tests for Flask application with API mocking and watchlist functionality
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_watchlist():
    """Reset watchlist before each test to ensure isolation"""
    from app import watchlist as wl
    wl.clear()
    yield
    wl.clear()


class TestDevOpsFlixComprehensiveFeatureTests:
    """DevOps Flix Comprehensive Feature Tests"""

    def test_should_render_homepage_with_trending_and_top_rated(self, client):
        """
        Mock the TMDB API response to ensure the homepage route '/'
        returns status 200 and renders correctly
        """
        mock_trending_data = {
            "results": [
                {
                    "id": 12345,
                    "title": "Mock Movie 1",
                    "overview": "This is a mock movie overview",
                    "poster_path": "/mock_poster.jpg",
                    "backdrop_path": "/mock_backdrop.jpg",
                    "vote_average": 8.5,
                    "release_date": "2024-01-15",
                },
                {
                    "id": 67890,
                    "title": "Mock Movie 2",
                    "overview": "Another mock movie",
                    "poster_path": "/mock_poster2.jpg",
                    "backdrop_path": "/mock_backdrop2.jpg",
                    "vote_average": 7.8,
                    "release_date": "2024-02-20",
                },
            ]
        }

        mock_top_rated_data = {
            "results": [
                {
                    "id": 11111,
                    "title": "Top Rated Mock",
                    "overview": "A top rated mock movie",
                    "poster_path": "/top_poster.jpg",
                    "backdrop_path": "/top_backdrop.jpg",
                    "vote_average": 9.2,
                    "release_date": "2023-12-01",
                }
            ]
        }

        def mock_get(url, params=None, timeout=None):
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()

            if "trending" in url:
                mock_response.json.return_value = mock_trending_data
            elif "top_rated" in url:
                mock_response.json.return_value = mock_top_rated_data
            else:
                mock_response.json.return_value = {"results": []}

            return mock_response

        with patch("app.requests.get", side_effect=mock_get):
            response = client.get("/")

            assert response.status_code == 200
            assert b"Trending" in response.data
            assert b"Top Rated" in response.data

    def test_should_add_movie_to_watchlist(self, client):
        """Add a dummy movie to watchlist and verify the list length increases"""
        from app import watchlist as wl

        assert len(wl) == 0

        movie_data = {
            "id": 99999,
            "title": "Test Movie for Watchlist",
            "poster_path": "/test_poster.jpg",
        }

        response = client.post(
            "/watchlist/add",
            json=movie_data,
            content_type="application/json",
        )

        assert response.status_code == 200

        response_data = response.get_json()
        assert response_data["success"] is True
        assert response_data["message"] == "Movie added to watchlist"
        assert len(wl) == 1
        assert wl[0]["id"] == 99999

    def test_should_remove_movie_from_watchlist(self, client):
        """Add a movie, then remove it, and verify the watchlist is empty"""
        from app import watchlist as wl

        movie_data = {
            "id": 88888,
            "title": "Movie to Remove",
            "poster_path": "/remove_poster.jpg",
        }

        add_response = client.post(
            "/watchlist/add",
            json=movie_data,
            content_type="application/json",
        )
        assert add_response.status_code == 200
        assert len(wl) == 1

        remove_response = client.post(
            "/watchlist/remove",
            json={"id": 88888},
            content_type="application/json",
        )

        assert remove_response.status_code == 200

        response_data = remove_response.get_json()
        assert response_data["success"] is True
        assert response_data["message"] == "Movie removed from watchlist"
        assert len(wl) == 0

    def test_should_fail_when_adding_duplicate_movie(self, client):
        """Test that adding a duplicate movie to watchlist fails"""
        from app import watchlist as wl

        movie_data = {
            "id": 77777,
            "title": "Duplicate Test Movie",
            "poster_path": "/dup_poster.jpg",
        }

        response1 = client.post(
            "/watchlist/add",
            json=movie_data,
            content_type="application/json",
        )
        assert response1.status_code == 200

        response2 = client.post(
            "/watchlist/add",
            json=movie_data,
            content_type="application/json",
        )
        assert response2.status_code == 400

        response_data = response2.get_json()
        assert response_data["success"] is False
        assert "already in watchlist" in response_data["message"]

        assert len(wl) == 1

    def test_should_return_404_when_removing_nonexistent_movie(self, client):
        """Test that removing a non-existent movie returns 404"""
        response = client.post(
            "/watchlist/remove",
            json={"id": 99999999},
            content_type="application/json",
        )

        assert response.status_code == 404
        response_data = response.get_json()
        assert response_data["success"] is False

    def test_should_return_json_results_for_search_endpoint(self, client):
        """Test the search endpoint returns proper JSON"""
        mock_search_data = {
            "results": [
                {
                    "id": 55555,
                    "title": "Searched Movie",
                    "poster_path": "/search_poster.jpg",
                    "vote_average": 7.5,
                    "media_type": "movie",  # Required for app.py filter
                }
            ]
        }

        def mock_get(url, params=None, timeout=None):
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = mock_search_data
            return mock_response

        with patch("app.requests.get", side_effect=mock_get):
            response = client.get("/api/search?q=test")

            assert response.status_code == 200
            data = response.get_json()
            assert "results" in data
            assert len(data["results"]) == 1

    def test_login_valid_user(self, client):
        """Test that login with valid credentials works and redirects to homepage"""
        login_data = {
            "username": "admin",
            "password": "123"
        }
        response = client.post("/login", data=login_data, follow_redirects=True)
        assert response.status_code == 200
        assert b"Trending" in response.data

    def test_login_invalid_user(self, client):
        """Test that login with invalid credentials shows error message"""
        login_data = {
            "username": "admin",
            "password": "wrongpassword"
        }
        response = client.post("/login", data=login_data, follow_redirects=True)
        assert response.status_code == 200
        assert b"Invalid credentials" in response.data

    def test_login_no_credentials(self, client):
        """Test that submitting empty credentials returns an error message"""
        login_data = {
            "username": "",
            "password": ""
        }
        response = client.post("/login", data=login_data, follow_redirects=True)
        assert response.status_code == 200
        assert b"Invalid credentials" in response.data

    def test_get_movie_details(self, client):
        """Test the movie detail page with streaming providers"""
        mock_movie_data = {
            "id": 12345,
            "title": "Mock Movie 1",
            "overview": "This is a mock movie overview",
            "poster_path": "/mock_poster.jpg",
            "backdrop_path": "/mock_backdrop.jpg",
            "vote_average": 8.5,
            "release_date": "2024-01-15",
            "runtime": 120,
            "genres": [{"name": "Action"}, {"name": "Adventure"}],
            "credits": {"cast": [], "crew": []},
            "videos": {"results": []},
            "tagline": "Test tagline",
            "status": "Released",
            "budget": 100000000,
            "revenue": 500000000,
            "vote_count": 1000
        }

        # Mock streaming provider data
        mock_providers = {
            "results": {
                "SG": {
                    "flatrate": [
                        {"provider_name": "Netflix", "logo_path": "/netflix_logo.jpg"},
                        {"provider_name": "Amazon", "logo_path": "/amazon_logo.jpg"}
                    ]
                }
            }
        }

        # Mock the TMDB API call for movie details and watch providers
        def mock_get(url, params=None, timeout=None):
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()

            if "watch/providers" in url:
                mock_response.json.return_value = mock_providers
            elif "movie" in url:
                mock_response.json.return_value = mock_movie_data

            return mock_response

        with patch("app.requests.get", side_effect=mock_get):
            response = client.get("/movie/12345")

            # Assert the status code is 200 (successful page load)
            assert response.status_code == 200

            # Assert that Netflix is in the response data (streaming provider)
            assert b"Netflix" in response.data

            # Assert that Amazon is in the response data (streaming provider)
            assert b"Amazon" in response.data

            # Assert that the section containing the streaming providers is present
            assert b"Stream Legally on:" in response.data
