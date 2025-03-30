"""WSGI Entry Point

This module serves as the entry point for WSGI servers (e.g., Gunicorn)
and development server. It imports the Flask application instance and
provides a standard WSGI interface.

For development:
    python wsgi.py

For production (using Gunicorn):
    gunicorn wsgi:app
"""

from app import app

if __name__ == '__main__':
    # Run the development server when executing this file directly
    app.run()
