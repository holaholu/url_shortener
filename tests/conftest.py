"""Test configuration and fixtures."""
import pytest
from unittest.mock import MagicMock
from redis import Redis

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """Mock Redis for all tests."""
    mock = MagicMock(spec=Redis)
    # Setup basic mock responses
    mock.get.return_value = None  # Default to no existing URL
    mock.set.return_value = True  # Default to successful set
    mock.delete.return_value = True  # Default to successful delete
    mock.ping.return_value = True  # Default to successful ping
    
    def mock_get(key):
        if key == b'https://www.example.com':
            return b'abc123'
        return None
    
    mock.get.side_effect = mock_get
    
    # Patch Redis in the app module
    monkeypatch.setattr('app.redis_client', mock)
    return mock
