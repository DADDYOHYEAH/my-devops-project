import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    # Check for our new bold title
    assert b"System Monitor" in response.data
    # Check for the dynamic Pod Identity label
    assert b"Pod Identity" in response.data
    # Check for the version badge
    assert b"V4.0 LIVE" in response.data

def test_feature(client):
    response = client.get('/feature')
    assert response.status_code == 200
    assert b"Neobrutalism" in response.data