# VI→EN Reflex Trainer - API Backend Design

**Date:** 2026-01-24  
**Status:** Approved  
**Author:** Design Session with User

## Overview

Transform the desktop VI→EN Reflex Trainer into a web application with RESTful API backend. The system supports both guest users (practice without login) and registered users (with progress tracking), plus admin dashboard for content management.

## Architecture

### Clean Architecture Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings (database, TTS, JWT...)
│   ├── dependencies.py      # Shared dependencies (DB session, auth)
│   │
│   ├── api/                 # API routes layer
│   │   └── v1/
│   │       ├── auth.py      # Login, register, refresh token
│   │       ├── lessons.py   # CRUD lessons
│   │       ├── sentences.py # CRUD sentences
│   │       ├── practice.py  # Get random/next sentence, record progress
│   │       ├── audio.py     # Generate/serve audio files
│   │       └── admin.py     # Admin-only endpoints
│   │
│   ├── models/              # SQLAlchemy models (database tables)
│   │   ├── user.py
│   │   ├── lesson.py
│   │   ├── sentence.py
│   │   ├── progress.py      # User practice history
│   │   └── audio_cache.py   # Track generated audio files
│   │
│   ├── schemas/             # Pydantic schemas (request/response validation)
│   │   ├── auth.py
│   │   ├── lesson.py
│   │   ├── sentence.py
│   │   └── practice.py
│   │
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── tts_service.py   # Audio generation logic
│   │   ├── practice_service.py
│   │   └── admin_service.py
│   │
│   └── core/                # Core utilities
│       ├── security.py      # JWT, password hashing
│       ├── database.py      # DB connection, session
│       └── exceptions.py    # Custom exceptions
│
├── migrations/              # Alembic migrations
├── tests/
├── requirements.txt
└── .env
```

**Design Principles:**
- **Separation of Concerns:** Routes, models, schemas, services separated
- **Dependency Injection:** FastAPI dependencies for DB session, auth
- **Reusability:** Business logic in services, reusable across endpoints
- **Testability:** Clear boundaries make unit testing straightforward

## Database Schema (PostgreSQL)

### Users Table
```sql
users
├── id (UUID, PK)
├── email (VARCHAR, UNIQUE, NOT NULL)
├── username (VARCHAR, UNIQUE, NOT NULL)
├── hashed_password (VARCHAR, NOT NULL)
├── is_active (BOOLEAN, DEFAULT TRUE)
├── is_admin (BOOLEAN, DEFAULT FALSE)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

### Lessons Table
```sql
lessons
├── id (INTEGER, PK, AUTO_INCREMENT)
├── title (VARCHAR, NOT NULL)
├── description (TEXT)
├── order_index (INTEGER, DEFAULT 0)
├── is_active (BOOLEAN, DEFAULT TRUE)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

### Sentences Table
```sql
sentences
├── id (INTEGER, PK, AUTO_INCREMENT)
├── lesson_id (INTEGER, FK -> lessons.id, CASCADE)
├── vi_text (TEXT, NOT NULL)
├── en_text (TEXT, NOT NULL)
├── order_index (INTEGER, DEFAULT 0)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

### Audio Files Table (Cache)
```sql
audio_files
├── id (INTEGER, PK, AUTO_INCREMENT)
├── sentence_id (INTEGER, FK -> sentences.id, CASCADE)
├── language (VARCHAR, 'vi' or 'en')
├── file_path (VARCHAR, UNIQUE)
├── file_size (INTEGER)
├── created_at (TIMESTAMP)
└── UNIQUE(sentence_id, language)
```

### User Progress Table
```sql
user_progress
├── id (INTEGER, PK, AUTO_INCREMENT)
├── user_id (UUID, FK -> users.id, CASCADE)
├── sentence_id (INTEGER, FK -> sentences.id, CASCADE)
├── practiced_count (INTEGER, DEFAULT 1)
├── last_practiced_at (TIMESTAMP)
├── created_at (TIMESTAMP)
├── updated_at (TIMESTAMP)
└── UNIQUE(user_id, sentence_id)
```

### Indexes
- `users(email)`, `users(username)`
- `sentences(lesson_id)`
- `user_progress(user_id, last_practiced_at)`
- `audio_files(sentence_id, language)`

## API Endpoints

### Pagination Standard (All List Endpoints)

**Query Parameters:**
- `page`: int = 1 (default)
- `limit`: int = 20 (default, max 100)
- `sort_by`: string (field name)
- `order`: asc|desc (default: asc)
- `search`: string (keyword search)

**Response Format:**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total_items": 150,
      "total_pages": 8,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### Authentication Endpoints (Public)
```
POST   /api/v1/auth/register          # Register new user
POST   /api/v1/auth/login             # Login (returns JWT tokens)
POST   /api/v1/auth/refresh           # Refresh access token
POST   /api/v1/auth/logout            # Logout (optional)
GET    /api/v1/auth/me                # Get current user info
```

### Lessons Endpoints
```
GET    /api/v1/lessons
       ?page=1&limit=20
       &search=keyword           # Search in title, description
       &sort_by=updated_at       # Options: title, created_at, updated_at, order_index
       &order=desc

GET    /api/v1/lessons/{id}           # Get lesson detail (public)
POST   /api/v1/lessons                # Create lesson (admin only)
PUT    /api/v1/lessons/{id}           # Update lesson (admin only)
DELETE /api/v1/lessons/{id}           # Delete lesson (admin only)
```

### Sentences Endpoints
```
GET    /api/v1/sentences
       ?lesson_id=1
       &page=1&limit=20
       &search=hello             # Search in vi_text, en_text
       &sort_by=updated_at       # Options: created_at, updated_at, order_index
       &order=desc

GET    /api/v1/sentences/{id}         # Get sentence detail
POST   /api/v1/sentences              # Create sentence (admin only)
PUT    /api/v1/sentences/{id}         # Update sentence (admin only)
DELETE /api/v1/sentences/{id}         # Delete sentence (admin only)
POST   /api/v1/sentences/bulk         # Bulk create from CSV (admin only)
```

### Practice Endpoints (User)
```
GET    /api/v1/practice/next
       ?lesson_id=1
       &mode=random               # Options: random, sequential

POST   /api/v1/practice/record        # Record practice session
       Body: { "sentence_id": 1 }

GET    /api/v1/practice/progress
       ?page=1&limit=20
       &lesson_id=1
       &sort_by=last_practiced_at
       &order=desc

GET    /api/v1/practice/stats         # User statistics
```

### Audio Endpoints
```
GET    /api/v1/audio/{sentence_id}/vi # Get Vietnamese audio
GET    /api/v1/audio/{sentence_id}/en # Get English audio
POST   /api/v1/audio/regenerate       # Force regenerate (admin only)
POST   /api/v1/audio/regenerate-all   # Regenerate all (admin only)
GET    /api/v1/audio/stats            # Audio cache statistics
```

### Admin Endpoints
```
GET    /api/v1/admin/stats            # Overall statistics
GET    /api/v1/admin/users
       ?page=1&limit=50
       &search=john@email.com    # Search in email, username
       &sort_by=updated_at
       &order=desc
       &is_active=true           # Filter by status
       &is_admin=false

PUT    /api/v1/admin/users/{id}       # Update user (activate/deactivate, grant admin)
```

### Default Sorting
- Lessons: `order_index ASC`
- Sentences: `order_index ASC`
- Users: `created_at DESC`
- Progress: `last_practiced_at DESC`

## Authentication & Security

### JWT Token Strategy
```
Access Token:
- Expires: 15 minutes
- Used for: API authentication
- Contains: user_id, email, is_admin

Refresh Token:
- Expires: 7 days
- Used for: Getting new access token
- Stored: HTTP-only cookie (secure)
```

### Authentication Flow
1. **Register/Login** → Returns access_token + refresh_token
2. **API calls** → Send `Authorization: Bearer {access_token}`
3. **Token expired** → Call `/auth/refresh` with refresh_token
4. **Guest mode** → No token required for public endpoints

### Security Features
- Password hashing: `bcrypt` (cost factor = 12)
- JWT signing: `HS256` algorithm
- CORS: Configurable allowed origins
- Rate limiting: 100 requests/minute per IP
- Input validation: Pydantic schemas

### Access Control
**Public (no auth):**
- GET /lessons, /sentences
- GET /audio/{id}/vi, /audio/{id}/en
- POST /auth/register, /auth/login

**User (requires auth):**
- GET /auth/me
- GET /practice/next
- POST /practice/record
- GET /practice/progress

**Admin only:**
- POST/PUT/DELETE /lessons, /sentences
- GET/PUT /admin/users
- POST /audio/regenerate

### Error Responses
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

## Audio Generation & Caching

### TTS Service Design
```python
Workflow:
1. Request audio for sentence_id + language
2. Check audio_files table (cache)
3. If exists → Return file path
4. If not exists:
   - Generate audio with gTTS
   - Save to /audio/{sentence_id}_{lang}.mp3
   - Insert record to audio_files table
   - Return file path
```

### Audio File Organization
```
audio/
├── 1_vi.mp3           # Sentence ID 1, Vietnamese
├── 1_en.mp3           # Sentence ID 1, English
├── 2_vi.mp3
├── 2_en.mp3
└── ...
```

### Audio API Response
```
GET /api/v1/audio/{sentence_id}/vi

Response:
- Content-Type: audio/mpeg
- Cache-Control: public, max-age=31536000 (1 year)
- Streams audio file directly
```

### Error Handling
- Sentence not found → 404 Not Found
- TTS generation fails → 500 Server Error, log error, retry
- Audio file corrupted → Delete from cache, regenerate
- gTTS network issue → Fallback to pyttsx3 (offline)

### Admin Features
- Regenerate single audio file
- Regenerate all audio files (background job)
- View cache statistics (total files, total size, hit rate)

## Practice Logic & Business Rules

### Get Next Sentence
```python
GET /api/v1/practice/next?lesson_id=1&mode=random

Logic (Authenticated User):
1. Get sentences from lesson
2. Filter out recently practiced (< 5 minutes ago)
3. Prioritize least practiced sentences
4. Return random sentence from filtered list

Logic (Guest):
1. Get sentences from lesson
2. Return random sentence (no tracking)

Response:
{
  "success": true,
  "data": {
    "sentence": {
      "id": 1,
      "vi_text": "Xin chào",
      "en_text": "Hello",
      "vi_audio_url": "/api/v1/audio/1/vi",
      "en_audio_url": "/api/v1/audio/1/en"
    },
    "progress": {
      "practiced_count": 3,
      "total_in_lesson": 50,
      "completion_percentage": 6
    }
  }
}
```

### Record Practice
```python
POST /api/v1/practice/record
Body: { "sentence_id": 1 }

Action:
- Insert/Update user_progress table
- Increment practiced_count
- Update last_practiced_at to now
```

### Practice Statistics
```python
GET /api/v1/practice/stats

Response:
{
  "total_practiced": 150,
  "unique_sentences": 45,
  "current_streak_days": 7,
  "lessons_completed": [1, 2],
  "recent_activity": [
    { "date": "2026-01-24", "count": 20 },
    { "date": "2026-01-23", "count": 15 }
  ]
}
```

## Configuration & Environment

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/reflex_trainer
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# JWT
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# TTS
TTS_ENGINE=gtts  # or pyttsx3
AUDIO_DIR=./audio
MAX_AUDIO_SIZE_MB=5

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100

# Admin
FIRST_ADMIN_EMAIL=admin@example.com
FIRST_ADMIN_PASSWORD=changeme123

# Server
API_V1_PREFIX=/api/v1
DEBUG=false
```

### Configuration Management
```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    cors_origins: list[str]
    # ... other settings
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Testing Strategy

### Test Structure
```
tests/
├── conftest.py              # Fixtures (test DB, test client)
├── test_auth.py             # Auth endpoints tests
├── test_lessons.py          # Lessons CRUD tests
├── test_sentences.py        # Sentences CRUD tests
├── test_practice.py         # Practice logic tests
├── test_audio.py            # Audio generation tests
└── test_permissions.py      # Authorization tests
```

### Testing Approach
- Use separate PostgreSQL database for testing
- Use pytest-asyncio for async tests
- Mock external dependencies (gTTS)
- Coverage target: >80%

## Error Handling

### Custom Exceptions
- NotFoundError → 404
- UnauthorizedError → 401
- ForbiddenError → 403
- ValidationError → 422
- DatabaseError → 500

### Global Exception Handler
- Log all errors with context
- Return consistent error response format
- Hide sensitive information in production
- Include request ID for tracing

### Logging
- Use structlog for structured logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log destinations: console (dev), file + monitoring (prod)
- Mask sensitive data: passwords, tokens

## Deployment

### Docker Support
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: reflex_trainer
      
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
```

### Deployment Steps
1. Setup PostgreSQL database
2. Run migrations: `alembic upgrade head`
3. Seed initial data from CSV
4. Create first admin user
5. Start API: `uvicorn app.main:app`
6. Setup reverse proxy (nginx)
7. Enable HTTPS (Let's Encrypt)
8. Monitor with Prometheus/Grafana (optional)

## Technical Stack

### Core Dependencies
- **FastAPI** - Modern async web framework
- **PostgreSQL** - Main database
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **python-jose** - JWT tokens
- **passlib** - Password hashing
- **gTTS** - Text-to-speech (primary)
- **pyttsx3** - Text-to-speech (fallback)
- **slowapi** - Rate limiting
- **pytest** - Testing

### Development Tools
- **uvicorn** - ASGI server
- **black** - Code formatting
- **flake8** - Linting
- **mypy** - Type checking

## Future Enhancements

### Phase 2 (Optional)
- Spaced repetition algorithm (SRS)
- Voice recognition for pronunciation practice
- Achievements and badges
- Social features (leaderboards, sharing)
- Mobile app (React Native)
- AI-powered sentence generation
- Export/import learning data

## Migration from Current System

### Data Migration
1. Export data from MySQL to CSV
2. Transform to PostgreSQL-compatible format
3. Import via bulk insert or Alembic seed script
4. Migrate existing audio files to new structure
5. Update file paths in audio_files table

### Backward Compatibility
- Desktop app can continue using MySQL
- API uses PostgreSQL independently
- Gradual transition: desktop → web over time

## Success Criteria

✅ Clean, modular code structure  
✅ Easy to extend with new features  
✅ Comprehensive test coverage  
✅ Good performance with pagination  
✅ Secure authentication and authorization  
✅ Efficient audio caching  
✅ Clear API documentation (auto-generated by FastAPI)  
✅ Docker-ready for easy deployment
