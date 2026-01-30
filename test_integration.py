"""
DevOps Flix - Integration Test Suite
End-to-end workflow tests for complete user journeys and multi-component interactions
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





class TestIntegrationWorkflows:
    """Integration Tests - Test complete user workflows and multi-component interactions"""

    def test_complete_user_journey_signup_to_watchlist(self, client):
        """
        Integration Test: Complete user journey from signup → login → search → watchlist
        Tests multiple components working together in a realistic user scenario
        """
        import sqlite3
        
        # Clear any existing test data from database

        
        # Also clear from database if exists
        try:
            conn = sqlite3.connect("devopsflix.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", ("integration_test_user",))
            cursor.execute("DELETE FROM watchlist WHERE user_id IN (SELECT id FROM users WHERE username = ?)", ("integration_test_user",))
            conn.commit()
            conn.close()
        except:
            pass  # Database might not exist yet, that's ok
        
        # Step 1: User signs up
        response = client.post('/signup', data={
            'email': 'testuser@devopsflix.com',
            'username': 'integration_test_user',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }, follow_redirects=True)
        assert response.status_code == 200
        # After signup, user should be redirected to login page
        assert b'Sign In' in response.data or b'sign in' in response.data.lower()
        # User should be in both database and in-memory dict
        # User should be in database (implicit by login success later)
        
        # Step 2: User logs in with new account
        response = client.post('/login', data={
            'username': 'integration_test_user',
            'password': 'testpass123'
        }, follow_redirects=True)
        assert response.status_code == 200
        # After successful login, user is redirected to index with trending content
        assert b'Trending' in response.data or b'trending' in response.data
        
        # Step 3: User adds movie to watchlist (session should persist from login)
        response = client.post('/watchlist/add', json={
            'id': 12345,
            'title': 'Integration Test Movie',
            'poster_path': '/integration_test.jpg'
        })
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['success'] is True
        # Check success message or response data instead of accessing in-memory list directly
        # Since we're using database for logged-in users, checking 'wl' will fail (it's empty)
        assert len(response_data['watchlist']) == 1
        
        # Step 4: User adds another movie
        response = client.post('/watchlist/add', json={
            'id': 67890,
            'title': 'Second Integration Movie',
            'poster_path': '/integration_test2.jpg'
        })
        assert response.status_code == 200
        response_data = response.get_json()
        assert len(response_data['watchlist']) == 2
        
        # Step 5: Verify watchlist contains both movies
        response = client.get('/watchlist')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['watchlist']) == 2
        # Database might return in different order (DESC by added_at)
        titles = [m['title'] for m in data['watchlist']]
        assert 'Integration Test Movie' in titles
        assert 'Second Integration Movie' in titles
        
        # Cleanup
        # Cleanup done by next test run or DB teardown


    def test_session_persistence_across_routes(self, client):
        """
        Integration Test: Session persistence when navigating between different routes
        Tests that login session is maintained across multiple page visits
        """
        import sqlite3
    
        # Ensure admin user exists for testing (DB should have it seeded)

            
        # Clean up admin's watchlist in DB to prevent duplicate errors
        try:
            conn = sqlite3.connect("devopsflix.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM watchlist WHERE user_id = (SELECT id FROM users WHERE username = 'admin') AND movie_id = 999")
            conn.commit()
            conn.close()
        except:
            pass
        
        # Step 1: Login with admin account
        response = client.post('/login', data={
            'username': 'admin',
            'password': '123'
        }, follow_redirects=False)
        
        # Should redirect after successful login
        assert response.status_code == 302
        
        # Step 2: Visit index page - session should persist
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200
        
        # Step 3: Visit search page - session should persist
        response = client.get('/search', follow_redirects=True)
        assert response.status_code == 200
        
        # Step 4: Add to watchlist - should work because logged in
        response = client.post('/watchlist/add', json={
            'id': 999,
            'title': 'Session Test Movie',
            'poster_path': '/session_test.jpg'
        })
        assert response.status_code == 200
        assert response.get_json()['success'] is True
        
        # Step 5: Logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        
        # Step 6: Watchlist operations should still work after logout
        # (current app doesn't require login for watchlist)
        response = client.post('/watchlist/add', json={
            'id': 888,
            'title': 'Post-Logout Movie',
            'poster_path': '/post_logout.jpg'
        })
        assert response.status_code == 401
        assert "Unauthorized" in response.get_json()["message"]

    def test_duplicate_prevention_in_workflow(self, client):
        """
        Integration Test: Duplicate prevention across multiple watchlist operations
        Tests that the system prevents duplicate movies in realistic usage
        """
        import sqlite3
        
        # Cleanup admin watchlist
        try:
            conn = sqlite3.connect("devopsflix.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM watchlist WHERE user_id = (SELECT id FROM users WHERE username = 'admin')")
            conn.commit()
            conn.close()
        except: pass
        
        # Login as admin
        client.post('/login', data={'username': 'admin', 'password': '123'})
        
        movie_data = {
            'id': 555,
            'title': 'Duplicate Prevention Test',
            'poster_path': '/dup_test.jpg'
        }
        
        # Step 1: Add movie for the first time
        response = client.post('/watchlist/add', json=movie_data)
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['success'] is True
        
        # Step 2: Try to add the same movie again
        response = client.post('/watchlist/add', json=movie_data)
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['success'] is False
        assert 'already in watchlist' in response_data['message']
        
        # Step 3: Verify watchlist still has only 1 movie
        response = client.get('/watchlist')
        data = response.get_json()
        assert len(data['watchlist']) == 1
        
        # Step 4: Add a different movie - should succeed
        response = client.post('/watchlist/add', json={
            'id': 556,
            'title': 'Different Movie',
            'poster_path': '/different.jpg'
        })
        assert response.status_code == 200
        data = client.get('/watchlist').get_json()
        assert len(data['watchlist']) == 2
        
        # Step 5: Try to add first movie again - should still fail
        response = client.post('/watchlist/add', json=movie_data)
        assert response.status_code == 400

    def test_failed_login_does_not_corrupt_session(self, client):
        """
        Integration Test: Failed login attempts don't corrupt session or break other features
        Tests system resilience when authentication fails
        """

        
        # Step 1: Try to login with wrong credentials
        response = client.post('/login', data={
            'username': 'nonexistent_user',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid credentials' in response.data
        
        # Step 2: Try multiple failed login attempts
        for i in range(3):
            response = client.post('/login', data={
                'username': f'fake_user_{i}',
                'password': f'fake_pass_{i}'
            })
            assert b'Invalid credentials' in response.data or response.status_code == 302
        
        # Step 3: Watchlist functionality should be blocked (401) because user is not logged in
        # This confirms that failed login did NOT accidentally create a session
        response = client.post('/watchlist/add', json={
            'id': 777,
            'title': 'Movie After Failed Login',
            'poster_path': '/after_fail.jpg'
        })
        assert response.status_code == 401

        
        # Step 4: Search should still work
        response = client.get('/search')
        assert response.status_code == 200
        
        # Step 5: Now login with correct credentials should work
        response = client.post('/login', data={
            'username': 'admin',
            'password': '123'
        }, follow_redirects=False)
        assert response.status_code == 302  # Redirect after successful login

    def test_search_to_watchlist_integration(self, client):
        """
        Integration Test: Search → View Results → Add to Watchlist workflow
        Tests integration between search API and watchlist functionality
        """
        import sqlite3
        
        # Cleanup admin watchlist
        try:
            conn = sqlite3.connect("devopsflix.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM watchlist WHERE user_id = (SELECT id FROM users WHERE username = 'admin')")
            conn.commit()
            conn.close()
        except: pass
        
        # Login as admin
        client.post('/login', data={'username': 'admin', 'password': '123'})
        
        # Mock TMDB API search response
        mock_search_data = {
            "results": [
                {
                    "id": 11111,
                    "title": "Search Integration Movie",
                    "poster_path": "/search_int.jpg",
                    "vote_average": 8.5,
                    "media_type": "movie",
                    "overview": "A test movie for integration testing"
                },
                {
                    "id": 22222,
                    "title": "Another Search Result",
                    "poster_path": "/search_int2.jpg",
                    "vote_average": 7.5,
                    "media_type": "movie",
                    "overview": "Second test movie"
                }
            ]
        }
        
        def mock_get(url, params=None, timeout=None):
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            
            if "search/multi" in url:
                mock_response.json.return_value = mock_search_data
            else:
                mock_response.json.return_value = {"results": []}
            
            return mock_response
        
        with patch("app.requests.get", side_effect=mock_get):
            # Step 1: User searches for a movie
            response = client.get('/api/search?q=integration')
            assert response.status_code == 200
            search_results = response.get_json()
            assert len(search_results['results']) == 2
            
            # Step 2: User selects first movie from search results
            first_movie = search_results['results'][0]
            assert first_movie['id'] == 11111
            assert first_movie['title'] == "Search Integration Movie"
            
            # Step 3: User adds first movie to watchlist
            response = client.post('/watchlist/add', json={
                'id': first_movie['id'],
                'title': first_movie['title'],
                'poster_path': first_movie['poster_path']
            })
            assert response.status_code == 200
            assert response.get_json()['success'] is True
            assert response.get_json()['success'] is True
            assert len(response.get_json()['watchlist']) == 1
            
            # Step 4: User adds second movie to watchlist
            second_movie = search_results['results'][1]
            response = client.post('/watchlist/add', json={
                'id': second_movie['id'],
                'title': second_movie['title'],
                'poster_path': second_movie['poster_path']
            })
            assert response.status_code == 200
            assert response.status_code == 200
            assert len(response.get_json()['watchlist']) == 2
            
            # Step 5: Verify both movies are in watchlist with correct data
            response = client.get('/watchlist')
            watchlist_data = response.get_json()['watchlist']
            assert len(watchlist_data) == 2
            assert watchlist_data[0]['id'] == 11111
            assert watchlist_data[1]['id'] == 22222
