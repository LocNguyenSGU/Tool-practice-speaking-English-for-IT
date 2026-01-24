# Vi-En Reflex Trainer - Backend API

RESTful API backend for Vietnamese-English reflex training application.

## 🚀 Quick Start

```bash
# 1. Install dependencies
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 3. Initialize database
alembic upgrade head
python scripts/seed_data.py  # Seeds 3 lessons + admin user

# 4. Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 📚 Tech Stack

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
DATABASE_URL=postgresql://user:pass@host:5432/db
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
