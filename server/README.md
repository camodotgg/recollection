# Recollection Backend - Phase 1 Complete

## What's Been Built

Phase 1 of the Recollection web platform is complete! We've implemented:

### ✅ Backend Foundation
- **FastAPI Application** with async support
- **PostgreSQL Database** with SQLAlchemy 2.0 (async ORM)
- **JWT Authentication** (access & refresh tokens)
- **User Management** (register, login, refresh, get user info)
- **Database Models** for Users, Content, Courses, and Task Status
- **Alembic Migrations** for database schema management
- **Docker Compose** for local development environment

### Project Structure

```
backend/
├── api/
│   ├── main.py              # FastAPI application
│   ├── routes/
│   │   └── auth.py          # Authentication endpoints
│   ├── dependencies.py      # JWT auth dependencies
├── db/
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy ORM models
│   └── migrations/          # Alembic migrations
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
├── security/
│   └── jwt.py               # JWT utilities
├── schemas/
│   └── auth.py              # Pydantic request/response models
└── requirements.txt
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.13+ (for local development without Docker)
- PostgreSQL 16+ (if running without Docker)
- Redis 7+ (if running without Docker)

### Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and set your values:
```bash
SECRET_KEY=<generate-with: openssl rand -hex 32>
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### Running with Docker (Recommended)

1. Start all services:
```bash
docker-compose up -d
```

2. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

3. Check logs:
```bash
docker-compose logs -f backend
```

4. Access the API:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Running Locally (Without Docker)

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Start PostgreSQL and Redis (manually or via Docker):
```bash
docker-compose up -d postgres redis
```

3. Run migrations:
```bash
alembic upgrade head
```

4. Start the server:
```bash
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication

#### Register User
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure-password-123"
}

Response: {
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure-password-123"
}

Response: {
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Refresh Token
```bash
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}

Response: {
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Get Current User
```bash
GET /auth/me
Authorization: Bearer <access_token>

Response: {
  "id": "uuid",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2025-11-25T12:00:00Z"
}
```

## Testing with curl

### Register a new user:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Login:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

Save the `access_token` from the response.

### Get current user:
```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <your-access-token>"
```

## Database Schema

### Users Table
- `id`: UUID (Primary Key)
- `email`: VARCHAR(255) UNIQUE
- `hashed_password`: VARCHAR
- `is_active`: BOOLEAN
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### Contents Table
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key → users.id)
- `source_link`: TEXT
- `source_author`: VARCHAR
- `source_origin`: VARCHAR
- `source_format`: ENUM (pdf, web, youtube, text)
- `summary_json`: JSONB (Pydantic Summary model)
- `raw_text`: TEXT
- `metadata_json`: JSONB
- `analyzed_json`: JSONB (AnalyzedContent with genre/topics)
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### Courses Table
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key → users.id)
- `title`: VARCHAR
- `description`: TEXT
- `objective`: TEXT
- `genre`: VARCHAR
- `difficulty_level`: ENUM (beginner, intermediate, advanced, expert)
- `lessons_json`: JSONB (Lesson[] Pydantic models)
- `takeaways_json`: JSONB
- `topics_json`: JSONB
- `completion_criteria_json`: JSONB
- `source_content_json`: JSONB
- `estimated_duration_seconds`: INTEGER
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### Task Status Table
- `task_id`: VARCHAR(255) (Primary Key)
- `user_id`: UUID (Foreign Key → users.id)
- `status`: ENUM (PENDING, STARTED, PROGRESS, SUCCESS, FAILURE)
- `progress_percent`: INTEGER
- `current_step`: VARCHAR
- `result_json`: JSONB
- `error_message`: TEXT
- `created_at`: TIMESTAMP
- `started_at`: TIMESTAMP
- `completed_at`: TIMESTAMP

## Development Commands

### Alembic (Database Migrations)

Create a new migration:
```bash
docker-compose exec backend alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
docker-compose exec backend alembic upgrade head
```

Rollback one migration:
```bash
docker-compose exec backend alembic downgrade -1
```

View migration history:
```bash
docker-compose exec backend alembic history
```

### Docker

Stop all services:
```bash
docker-compose down
```

Stop and remove volumes (⚠️ deletes data):
```bash
docker-compose down -v
```

View logs:
```bash
docker-compose logs -f backend
docker-compose logs -f postgres
```

Rebuild images:
```bash
docker-compose build backend
```

## Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**:
  - Access tokens: 30-minute expiry
  - Refresh tokens: 7-day expiry
- **CORS**: Configured for frontend origins
- **Input Validation**: Pydantic models for all requests
- **SQL Injection Protection**: SQLAlchemy parameterized queries

## What's Next - Phase 2

Phase 2 will implement:
- Celery background workers for long-running LLM tasks
- Content loading tasks (calls existing `src.content.loader.magic.load()`)
- Course generation tasks (calls existing `src.course.generator.generate_course()`)
- Task status tracking and polling endpoint
- Integration with existing Recollection business logic

## Troubleshooting

### Port already in use
If port 8000, 5432, or 6379 is already in use, modify the ports in `docker-compose.yml`.

### Database connection errors
Ensure PostgreSQL is running and the DATABASE_URL is correct in `.env`.

### Migration errors
Reset the database and rerun migrations:
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

### Import errors
Ensure you're running from the project root directory:
```bash
cd /path/to/recollection
uvicorn backend.api.main:app --reload
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
