"""URL Shortener Application Initialization

This module initializes the Flask application and sets up the Redis client.
It handles configuration through environment variables with sensible defaults
for development. For production, all values should be set in environment
variables or .env file.

Environment Variables:
    SECRET_KEY: Flask secret key for session management
    REDIS_HOST: Redis server hostname (default: localhost)
    REDIS_PORT: Redis server port (default: 6379)
    REDIS_PASSWORD: Redis password if required (default: None)

Note:
    The Redis client is configured to automatically decode responses to
    strings, which is necessary for URL storage and retrieval.
"""

from flask import Flask
from redis import Redis
import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Configure Flask secret key for session management
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Redis configuration with environment variables and development defaults
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_password = os.getenv('REDIS_PASSWORD', None)

# Initialize Redis client with automatic response decoding
redis_client = Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True  # Automatically decode bytes to strings
)

# Import routes after app initialization to avoid circular imports
from app import routes
