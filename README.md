# Book Manager Application

A FastAPI-based web application for managing books and tasks with user authentication.

## Features

- User authentication (register/login)
- Book management with filtering capabilities
- Task management with status tracking
- Responsive web interface

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Set up environment variables:
```bash
cp .env.example .env
```
The default values in .env should work out of the box with Docker.

3. Build and start the containers:
```bash
docker-compose up --build
```

4. Access the application:
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Container Architecture

The application runs in two containers:

1. **Web Application (web)**
   - FastAPI application
   - Serves the frontend
   - Handles API requests

2. **Database (db)**
   - PostgreSQL 15
   - Persists data using Docker volumes
   - Runs with health checks

## Development

### Running the Application

```bash
# Start the application
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild containers after changes
docker-compose up --build
```

### Database Management

```bash
# Access PostgreSQL CLI
docker-compose exec db psql -U postgres -d bookmanager

# Restart database container
docker-compose restart db

# View database logs
docker-compose logs db
```

### Troubleshooting

1. If the application fails to start:
   - Check if PostgreSQL container is healthy:
     ```bash
     docker-compose ps
     ```
   - View logs for specific issues:
     ```bash
     docker-compose logs web
     docker-compose logs db
     ```

2. If you need to reset the database:
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

## Environment Variables

Key variables in .env file:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=bookmanager
DATABASE_URL=postgresql://postgres:postgres@db:5432/bookmanager

SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API Documentation

Once running, you can access:
- Web Interface → http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests
pytest test_api.py
All API routes, authentication, and database operations are unit tested using TestClient

Environment Variables (.env)

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=bookmanager

# SQLAlchemy URL for app use
DATABASE_URL=postgresql://postgres:postgres@db:5432/bookmanager

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30


## Common Docker Commands
# Start the app
docker-compose up

# Rebuild after changes
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop + remove containers
docker-compose down

# Reset volumes (data loss)
docker-compose down -v


## License

MIT

## Author

Pranav Asalekar