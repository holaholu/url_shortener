# URL Shortener

A simple and efficient URL shortener service built with Flask and Redis.

## Features

- Shorten long URLs to manageable links
- Modern, responsive UI with Tailwind CSS
- Redis for fast and efficient storage
- Copy-to-clipboard functionality
- Input validation and error handling
- Duplicate URL detection

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: Redis
- **Frontend**: HTML, JavaScript, Tailwind CSS
- **Deployment**: Render.com

## Local Development

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Create .env file with:
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=your_password  # If required
   SECRET_KEY=your_secret_key
   ```

4. Run Redis (make sure Redis is installed):
   ```bash
   redis-server
   ```

5. Run the application:
   ```bash
   python wsgi.py
   ```

## Deployment

This application is configured for deployment on Render.com. Required environment variables:

- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_PASSWORD`
- `SECRET_KEY`

## License

MIT License
