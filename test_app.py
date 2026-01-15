import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_game_loads(client):
    """Test 1: Does the Huge Game File load?"""
    response = client.get('/')
    assert response.status_code == 200
    # We check for a common tag to make sure HTML is serving
    assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data

def test_dashboard(client):
    """Test 2: Does the Dashboard work?"""
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"DevOps Dashboard" in response.data