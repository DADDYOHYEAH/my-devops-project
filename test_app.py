import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hello!" in response.data

def test_feature(client):
    response = client.get('/feature')
    assert response.status_code == 200
    assert b"THIS WILL FAIL" in response.data