import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    """Test the Valentine Page loads"""
    response = client.get('/')
    assert response.status_code == 200
    # Check for text that is actually on your new page
    assert b"Will you be my Valentine?" in response.data

def test_yes_page(client):
    """Test the Yes Page loads"""
    response = client.get('/yes_page.html')
    assert response.status_code == 200
    assert b"Knew you would say yes!" in response.data

def test_dashboard(client):
    """Test that the DevOps Dashboard still works"""
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Ops Dashboard" in response.data