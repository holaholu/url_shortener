import pytest
from app import create_app
from app.routes import is_valid_url

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that home page loads successfully"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'URL Shortener' in rv.data

def test_valid_url():
    """Test URL validation"""
    assert is_valid_url('https://www.google.com')[0] is True
    assert is_valid_url('not-a-url')[0] is False

def test_shorten_url(client):
    """Test URL shortening"""
    data = {'url': 'https://www.example.com'}
    response = client.post('/shorten', json=data)
    assert response.status_code == 200
    assert 'short_url' in response.json
