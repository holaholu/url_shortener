"""Test Redis connection with production credentials."""
import os
from redis import Redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Redis configuration
redis_host = os.getenv('REDIS_HOST')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_password = os.getenv('REDIS_PASSWORD')

print(f"Attempting to connect to Redis at {redis_host}:{redis_port}")

try:
    # Initialize Redis client
    redis_client = Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True,
        socket_timeout=5
    )
    
    # Test connection
    response = redis_client.ping()
    print("✅ Successfully connected to Redis!")
    print(f"Ping response: {response}")
    
    # Test set and get
    print("\nTesting basic operations:")
    redis_client.set('test_key', 'test_value')
    value = redis_client.get('test_key')
    print(f"Set and retrieved test value: {value}")
    
    # Clean up
    redis_client.delete('test_key')
    print("Test completed and cleaned up!")
    
except Exception as e:
    print(f"❌ Error connecting to Redis: {str(e)}")
    print("\nDebug information:")
    print(f"Redis Host: {redis_host}")
    print(f"Redis Port: {redis_port}")
    print("Redis Password: [hidden]")
