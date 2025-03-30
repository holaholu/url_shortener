from flask import Flask
from redis import Redis
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Redis configuration
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_password = os.getenv('REDIS_PASSWORD', None)

redis_client = Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True
)

from app import routes
