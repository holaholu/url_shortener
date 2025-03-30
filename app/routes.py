"""URL Shortener Routes Module

This module handles all the routes and business logic for the URL shortener application.
It includes URL validation, shortening, redirection, and deletion functionality.

The module uses Redis for storing URL mappings with two types of keys:
- 'id:{short_id}' -> original URL
- 'url:{original_url}' -> short_id

This bidirectional mapping allows for efficient lookups and prevents duplicate URLs.
"""

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

# Suppress SSL verification warnings as we handle them explicitly in is_valid_url
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def generate_short_id(length=6):
    """Generate a random short ID for URL shortening.
    
    Args:
        length (int): Length of the generated ID. Defaults to 6.
        
    Returns:
        str: A random string containing letters and numbers.
        
    Note:
        With length=6, we get 62^6 possible combinations (56+ billion),
        which is sufficient for most use cases.
    """
    chars = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choice(chars) for _ in range(length))

def is_valid_url(url):
    """Validate a URL by checking its format and accessibility.
    
    This function performs two levels of validation:
    1. Structural validation: Checks if the URL has a valid scheme and netloc
    2. Accessibility validation: Attempts to make a HEAD request to verify the URL exists
    
    Args:
        url (str): The URL to validate
        
    Returns:
        tuple: (bool, str)
            - bool: True if URL is valid and accessible, False otherwise
            - str: None if valid, error message if invalid
            
    Note:
        - Uses HEAD request to minimize data transfer
        - Follows redirects to handle URL shorteners and redirects
        - Ignores SSL verification to handle self-signed certificates
        - Times out after 5 seconds to prevent hanging
    """
    try:
        # First check if URL is well-formed
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "Invalid URL format"
        
        # Try to make a HEAD request to check if the webpage exists
        response = requests.head(
            url,
            timeout=5,  # Prevent hanging on slow responses
            verify=False,  # Handle invalid SSL certificates
            allow_redirects=True  # Follow redirects
        )
        
        # Accept 2xx (success) and 3xx (redirect) status codes
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
    """Render the main page of the URL shortener.
    
    Returns:
        str: Rendered HTML template for the index page
    """
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Shorten a URL and store it in Redis.
    
    This endpoint handles the URL shortening process:
    1. Validates the input URL
    2. Checks for existing shortened version
    3. Generates a new short ID if needed
    4. Stores the mapping in Redis
    
    Returns:
        Response: JSON containing:
            - short_url: Full URL for redirection
            - short_id: The generated short ID
            - original_url: The original URL
            
        Status codes:
            - 200: Success
            - 400: Invalid URL or missing input
    """
    original_url = request.form.get('url')
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Add scheme if not present for proper validation
    if not urlparse(original_url).scheme:
        original_url = 'http://' + original_url
    
    # Validate the URL
    is_valid, error_message = is_valid_url(original_url)
    if not is_valid:
        return jsonify({'error': error_message}), 400

    # Check for existing shortened URL to prevent duplicates
    existing_short_id = redis_client.get(f'url:{original_url}')
    if existing_short_id:
        short_id = existing_short_id
    else:
        # Generate a new unique short ID
        while True:
            short_id = generate_short_id()
            if not redis_client.exists(f'id:{short_id}'):
                break

    # Store bidirectional mappings in Redis
    redis_client.set(f'id:{short_id}', original_url)
    if not existing_short_id:
        redis_client.set(f'url:{original_url}', short_id)

    # Return the shortened URL and metadata
    return jsonify({
        'short_url': url_for('redirect_to_url', short_id=short_id, _external=True),
        'short_id': short_id,
        'original_url': original_url
    })

@app.route('/<short_id>')
def redirect_to_url(short_id):
    """Redirect to the original URL from a short ID.
    
    Args:
        short_id (str): The short ID to look up
        
    Returns:
        Response: Redirect to original URL or index page if not found
        
    Note:
        If the short ID is not found, the user is redirected to the index
        page with a flash message indicating the error.
    """
    original_url = redis_client.get(f'id:{short_id}')
    if original_url is None:
        flash('URL not found')
        return redirect(url_for('index'))
    return redirect(original_url)

@app.route('/<short_id>', methods=['DELETE'])
def delete_url(short_id):
    """Delete a shortened URL mapping.
    
    This endpoint removes both the forward (id -> url) and reverse
    (url -> id) mappings from Redis.
    
    Args:
        short_id (str): The short ID to delete
        
    Returns:
        Response: Empty response with status code
            - 204: Successfully deleted
            - 404: URL not found
            
    Note:
        Recent URLs list is managed client-side in localStorage
    """
    # Get original URL for reverse mapping deletion
    original_url = redis_client.get(f'id:{short_id}')
    if original_url is None:
        return jsonify({'error': 'URL not found'}), 404

    # Remove both mappings from Redis
    redis_client.delete(f'id:{short_id}')
    redis_client.delete(f'url:{original_url}')

    return '', 204
