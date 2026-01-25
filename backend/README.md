# Vi-En Reflex Trainer - Backend API

RESTful API backend for Vietnamese-English reflex training application.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
cd backend
chmod +x setup.sh run.sh
./setup.sh      # Auto-setup everything
./run.sh        # Start server
```

### Option 2: Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Run migrations
alembic upgrade head

# 5. Seed data (optional)
python scripts/seed_data.py

# 6. Start server
uvicorn app.main:app --reload
```

**Access**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

**Default Admin**:
- Email: `admin@example.com`
- Password: `changeme123`

## 📚 Tech Stack

- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL + SQLAlchemy 2.0.25
- **Auth**: JWT + bcrypt
- **TTS**: gTTS (Google Text-to-Speech)
- **Migrations**: Alembic
- **Testing**: pytest

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── api/v1/              # API endpoints
│   │   ├── auth.py          # Authentication
│   │   ├── lessons.py       # Lessons CRUD
│   │   ├── sentences.py     # Sentences CRUD
│   │   ├── audio.py         # TTS generation
│   │   └── practice.py      # Practice logic
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   └── services/            # Business logic
├── migrations/              # Alembic migrations
├── scripts/                 # Utility scripts
└── tests/                   # API tests
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Lessons
- `GET /api/v1/lessons` - List lessons (with pagination)
- `GET /api/v1/lessons/{id}` - Get lesson details
- `POST /api/v1/lessons` - Create lesson (admin)
- `PUT /api/v1/lessons/{id}` - Update lesson (admin)
- `DELETE /api/v1/lessons/{id}` - Delete lesson (admin)

### Sentences
- `GET /api/v1/sentences` - List sentences
- `GET /api/v1/sentences/{id}` - Get sentence
- `POST /api/v1/sentences` - Create sentence (admin)
- `POST /api/v1/sentences/bulk` - Bulk create (admin)
- `PUT /api/v1/sentences/{id}` - Update sentence (admin)
- `DELETE /api/v1/sentences/{id}` - Delete sentence (admin)

### Audio
- `GET /api/v1/audio/{id}/{lang}` - Get audio file (vi/en)
- `DELETE /api/v1/audio/{id}` - Clear audio cache

### Practice
- `GET /api/v1/practice/next` - Get next sentence
- `POST /api/v1/practice/record` - Record practice session
- `GET /api/v1/practice/stats` - Get user statistics

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app tests/

# Specific test
pytest tests/test_api.py::test_login -v
```

## 🗄️ Database

**Current Setup**:
- PostgreSQL on Docker (port 5433)
- Database: `vi_en_trainer`
- User: `postgres`
- Password: `mysecretpassword`

**Migrations**:
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🚀 Production Deployment

### 1. Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Update .env
```env
SECRET_KEY=<generated-key>
DATABASE_URL=postgresql://user:pass@host:5433/db
CORS_ORIGINS=https://yourdomain.com
DEBUG=False
```

### 3. Run with Gunicorn
```bash
./run.sh --prod --workers 4
```

## 📝 Environment Variables

Key variables in `.env`:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret (min 32 chars)
- `ALGORITHM` - JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry
- `CORS_ORIGINS` - Allowed origins (comma-separated)
- `DEBUG` - Debug mode (True/False)

See `.env.example` for full list.

## 🔧 Useful Commands

```bash
# Development server
./run.sh

# Production server
./run.sh --prod

# Different port
./run.sh --port 3000

# Database seed
python scripts/seed_data.py

# Run migrations
alembic upgrade head

# Run tests
pytest -v
```

## 📖 Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Authentication Flow

1. **Register**: `POST /api/v1/auth/register`
2. **Login**: `POST /api/v1/auth/login` → Get `access_token`
3. **Use Token**: Add header `Authorization: Bearer <token>`
4. **Refresh**: `POST /api/v1/auth/refresh` with `refresh_token`

## 🎯 Key Features

- **Hybrid Mode**: Guest browsing + User progress tracking
- **Smart Algorithm**: Spaced repetition for practice
- **Audio Generation**: On-demand TTS with caching
- **Rate Limiting**: 100 requests/minute
- **Admin Panel**: Content management via API

## 📦 Dependencies

Main packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `psycopg2-binary` - PostgreSQL driver
- `alembic` - Database migrations
- `python-jose` - JWT handling
- `passlib[bcrypt]` - Password hashing
- `gtts` - Text-to-speech
- `pytest` - Testing framework

See `requirements.txt` for complete list.

## 🐛 Troubleshooting

**Port already in use**:
```bash
kill -9 $(lsof -ti:8000)
```

**Database connection error**:
- Check PostgreSQL is running: `docker ps`
- Verify credentials in `.env`
- Test connection: `psql -h localhost -p 5433 -U postgres -d vi_en_trainer`

**Migration errors**:
```bash
alembic stamp head
alembic revision --autogenerate -m "fix"
alembic upgrade head
```

## 📄 License

MIT License - See LICENSE file for details

- **Framework**: FastAPI 0.109.0 (async, auto-docs)
- **Database**: PostgreSQL + SQLAlchemy 2.0.25
- **Auth**: JWT (python-jose) + bcrypt passwords
- **TTS**: gTTS (online) + pyttsx3 (offline fallback)
- **Migrations**: Alembic 1.13.1
- **Testing**: pytest 7.4.4 + httpx
- **Rate Limiting**: slowapi 0.1.9

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app + middleware
│   ├── config.py            # Pydantic Settings
│   ├── dependencies.py      # Auth dependencies
│   ├── api/v1/             # API endpoints
│   │   ├── auth.py         # Register/login/refresh
│   │   ├── lessons.py      # CRUD + pagination
│   │   ├── sentences.py    # CRUD + bulk create
│   │   ├── audio.py        # TTS generation
│   │   └── practice.py     # Smart algorithm + stats
│   ├── core/               # Core utilities
│   │   ├── database.py     # SQLAlchemy setup
│   │   ├── security.py     # JWT + password hashing
│   │   └── exceptions.py   # Custom exceptions
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   └── services/           # Business logic
├── migrations/             # Alembic migrations
├── scripts/seed_data.py    # Database seeding
├── tests/test_api.py       # API tests
└── requirements.txt
```

## 🔐 Authentication

**Register**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"pass123"}'
```

**Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"user@example.com","password":"pass123"}'
```

**Use Token**:
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your_access_token>"
```

## 🎯 Key Features

### Hybrid Mode (Guest + Registered)
- **Guests**: Browse lessons, practice, audio (no auth required)
- **Users**: Progress tracking + statistics
- **Admins**: Content management (CRUD)

### Smart Practice Algorithm
```python
# Authenticated users:
- Filters out recently practiced (< 5 min)
- Returns least practiced sentence first
- Includes progress stats

# Guests:
- Random sentence selection
```

### Audio Generation
- **On-demand TTS** with file caching
- **Primary**: gTTS (Google, high quality)
- **Fallback**: pyttsx3 (offline, lower quality)
- **Format**: MP3, 24kbps
- Auto-invalidation on sentence updates

## 📡 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| **Authentication** ||||
| POST | `/api/v1/auth/register` | None | Register user |
| POST | `/api/v1/auth/login` | None | Login |
| POST | `/api/v1/auth/refresh` | None | Refresh token |
| GET | `/api/v1/auth/me` | User | Current user info |
| **Lessons** ||||
| GET | `/api/v1/lessons` | Guest | List (pagination, search) |
| GET | `/api/v1/lessons/{id}` | Guest | Lesson details |
| POST | `/api/v1/lessons` | Admin | Create lesson |
| PUT | `/api/v1/lessons/{id}` | Admin | Update lesson |
| DELETE | `/api/v1/lessons/{id}` | Admin | Delete (cascade) |
| **Sentences** ||||
| GET | `/api/v1/sentences` | Guest | List (pagination, filter) |
| GET | `/api/v1/sentences/{id}` | Guest | Sentence + audio URLs |
| POST | `/api/v1/sentences` | Admin | Create sentence |
| POST | `/api/v1/sentences/bulk` | Admin | Bulk create |
| PUT | `/api/v1/sentences/{id}` | Admin | Update sentence |
| DELETE | `/api/v1/sentences/{id}` | Admin | Delete sentence |
| **Audio** ||||
| GET | `/api/v1/audio/{id}/{lang}` | Guest | Get MP3 (vi/en) |
| DELETE | `/api/v1/audio/{id}` | Guest | Clear cache |
| **Practice** ||||
| GET | `/api/v1/practice/next` | Guest | Next sentence (smart) |
| POST | `/api/v1/practice/record` | Guest | Record session |
| GET | `/api/v1/practice/stats` | User | User statistics |

**Query params**: `?page=1&page_size=10&search=hello&lesson_id=1`

## 🧪 Testing

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# With coverage
pytest --cov=app tests/

# Specific test
pytest tests/test_api.py::test_register_user -v
```

**Test Coverage**:
- ✅ Health check
- ✅ Registration (success, duplicate)
- ✅ Login (success, invalid)
- ✅ Protected endpoints
- ✅ Lessons CRUD + pagination
- ✅ Practice flow (guest + user)

## 🗄️ Database

### Models
```
User (UUID)
  └─> Progress ─> Sentence

Lesson
  └─> Sentence (cascade delete)
      ├─> AudioFile (cascade delete)
      └─> Progress (cascade delete)
```

### Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1

# Check current
alembic current
```

## 🚀 Production Deployment

### 1. Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Update .env
```env
SECRET_KEY=<generated-key>
DATABASE_URL=postgresql://user:pass@host:5433/db
CORS_ORIGINS=https://yourdomain.com
```

### 3. Deploy with Gunicorn
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 4. Nginx Config
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. SSL with Certbot
```bash
sudo certbot --nginx -d api.yourdomain.com
```

## 🐛 Troubleshooting

**Database connection error**:
```bash
# Check PostgreSQL
sudo service postgresql status

# Test connection
psql -U user -d reflex_trainer -h localhost
```

**Audio generation fails**:
```bash
# macOS
brew install espeak

# Linux
sudo apt-get install espeak

# Test
python -c "from gtts import gTTS; gTTS('test', lang='vi').save('test.mp3')"
```

**Migration conflicts**:
```bash
alembic stamp head
alembic revision --autogenerate -m "fix"
alembic upgrade head
```

## 📝 License

MIT

## Project Structure

See design doc: `/docs/plans/2026-01-24-api-backend-design.md`
