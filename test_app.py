import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    """Test the Home Page loads and shows the welcome message"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to V4.0" in response.data
    assert b"MY_DEVOPS_PROJECT" in response.data

def test_dashboard(client):
    """Test the Dashboard Page loads and shows system info"""
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"System Monitor" in response.data
    assert b"POD ID" in response.data

def test_team(client):
    """Test the Team Page loads"""
    response = client.get('/team')
    assert response.status_code == 200
    assert b"Meet the Team" in response.data