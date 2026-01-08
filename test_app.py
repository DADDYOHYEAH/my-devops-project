import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    # Check for the new title in the HTML
    assert b"DevOps Dashboard" in response.data
    # Check if the "Pod ID" label is present
    assert b"Running on Pod ID" in response.data

def test_feature(client):
    response = client.get('/feature')
    assert response.status_code == 200
    assert b"Marketing Feature" in response.data