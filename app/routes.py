from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, redis_client
import string
import random
import validators
import json
from urllib.parse import urlparse
from datetime import datetime
import requests
from requests.exceptions import RequestException
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def generate_short_id(length=6):
    """Generate a random string of fixed length"""
    chars = string.ascii_letters + string.digits #This is a string of all the characters
    return ''.join(random.choice(chars) for _ in range(length))

def is_valid_url(url):
    """Check if the URL is valid, has a scheme, and points to an accessible webpage"""
    try:
        # First check if URL is well-formed
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "Invalid URL format"
        
        # Try to make a HEAD request to check if the webpage exists
        # Set a timeout to avoid hanging on slow responses
        # Verify=False to handle sites with invalid SSL certificates
        # Allow_redirects=True to follow redirects
        response = requests.head(
            url,
            timeout=5,
            verify=False,
            allow_redirects=True
        )
        
        # Check if the response status code indicates success (200-299) or redirection (300-399)
        if 200 <= response.status_code < 400:
            return True, None
        else:
            return False, f"URL returned status code {response.status_code}"
            
    except requests.exceptions.Timeout:
        return False, "URL took too long to respond"
    except requests.exceptions.SSLError:
        return False, "SSL certificate verification failed"
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the website"
    except RequestException as e:
        return False, f"Error accessing URL: {str(e)}"
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form.get('url')
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Add scheme if not present
    if not urlparse(original_url).scheme:
        original_url = 'http://' + original_url
    
    is_valid, error_message = is_valid_url(original_url)
    if not is_valid:
        return jsonify({'error': error_message}), 400

    # Check if URL already exists
    existing_short_id = redis_client.get(f'url:{original_url}')
    if existing_short_id:
        short_id = existing_short_id
    else:
        # Generate a new short ID
        while True:
            short_id = generate_short_id()
            if not redis_client.exists(f'id:{short_id}'):
                break

    # Store mappings in Redis
    redis_client.set(f'id:{short_id}', original_url)
    if not existing_short_id:
        redis_client.set(f'url:{original_url}', short_id)

    # No need to store in recent URLs list as it's handled by client

    return jsonify({
        'short_url': url_for('redirect_to_url', short_id=short_id, _external=True),
        'short_id': short_id,
        'original_url': original_url
    })

@app.route('/<short_id>')
def redirect_to_url(short_id):
    original_url = redis_client.get(f'id:{short_id}')
    if original_url is None:
        flash('URL not found')
        return redirect(url_for('index'))
    return redirect(original_url)

@app.route('/<short_id>', methods=['DELETE'])
def delete_url(short_id):
    # Get original URL
    original_url = redis_client.get(f'id:{short_id}')
    if original_url is None:
        return jsonify({'error': 'URL not found'}), 404

    # Remove from Redisl
    redis_client.delete(f'id:{short_id}')
    redis_client.delete(f'url:{original_url}')

    # No need to remove from recent URLs list as it's handled by client

    return '', 204
