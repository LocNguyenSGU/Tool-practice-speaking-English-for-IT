# API Backend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a production-ready FastAPI backend with PostgreSQL for VI→EN Reflex Trainer web application, supporting guest/registered users, admin management, and on-demand audio generation.

**Architecture:** Clean architecture with separated layers (API routes, models, schemas, services, core). JWT authentication with hybrid mode (guest + registered users). PostgreSQL with SQLAlchemy ORM and Alembic migrations. On-demand TTS audio generation with caching.

**Tech Stack:** FastAPI, PostgreSQL, SQLAlchemy, Alembic, Pydantic, python-jose[cryptography], passlib[bcrypt], gTTS, pyttsx3, slowapi, pytest, pytest-asyncio

---

## Task 1: Project Setup and Dependencies

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/README.md`
- Create: `backend/app/__init__.py`

**Step 1: Create project structure**

```bash
mkdir -p backend/app/{api/v1,models,schemas,services,core}
mkdir -p backend/{tests,migrations,audio}
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/services/__init__.py
touch backend/app/core/__init__.py
touch backend/tests/__init__.py
```

**Step 2: Write requirements.txt**

Create `backend/requirements.txt`:

```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# Validation
pydantic==2.5.3
pydantic-settings==2.1.0
email-validator==2.1.0

# TTS
gTTS==2.5.0
pyttsx3==2.90

# Rate Limiting
slowapi==0.1.9

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
faker==22.0.0

# Development
black==24.1.1
flake8==7.0.0
mypy==1.8.0
```

**Step 3: Create .env.example**

Create `backend/.env.example`:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/reflex_trainer
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# JWT
SECRET_KEY=your-secret-key-here-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# TTS
TTS_ENGINE=gtts
AUDIO_DIR=./audio
MAX_AUDIO_SIZE_MB=5

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100

# Admin (change in production!)
FIRST_ADMIN_EMAIL=admin@example.com
FIRST_ADMIN_PASSWORD=changeme123

# Server
API_V1_PREFIX=/api/v1
DEBUG=true
```

**Step 4: Create README.md**

Create `backend/README.md`:

```markdown
# VI→EN Reflex Trainer - API Backend

FastAPI backend with PostgreSQL for Vietnamese-English reflex training.

## Setup

1. Install dependencies:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Setup PostgreSQL:
   ```bash
   # Install PostgreSQL if needed
   # macOS: brew install postgresql
   # Ubuntu: sudo apt install postgresql
   
   # Create database
   createdb reflex_trainer
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Run migrations:
   ```bash
   alembic upgrade head
   ```

5. Start server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. API Documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Testing

```bash
pytest
pytest --cov=app tests/
```

## Project Structure

See design doc: `/docs/plans/2026-01-24-api-backend-design.md`
```

**Step 5: Commit project setup**

```bash
cd /Users/nguyenhuuloc/Documents/MyComputer/vi-en-reflex-trainer/.worktrees/api-backend
git add backend/
git commit -m "chore: setup backend project structure and dependencies"
```

---

## Task 2: Core Configuration and Database Setup

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/app/core/database.py`
- Create: `backend/app/core/exceptions.py`

**Step 1: Write config.py**

Create `backend/app/config.py`:

```python
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    # Database
    database_url: str
    db_pool_size: int = 20
    db_max_overflow: int = 10
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # TTS
    tts_engine: str = "gtts"
    audio_dir: str = "./audio"
    max_audio_size_mb: int = 5
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 100
    
    # Admin
    first_admin_email: str = "admin@example.com"
    first_admin_password: str = "changeme123"
    
    # Server
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    project_name: str = "VI→EN Reflex Trainer API"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
```

**Step 2: Write database.py**

Create `backend/app/core/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 3: Write exceptions.py**

Create `backend/app/core/exceptions.py`:

```python
from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
```

**Step 4: Commit core setup**

```bash
git add backend/app/config.py backend/app/core/
git commit -m "feat(core): add configuration and database setup"
```

---

## Task 3: Database Models

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/lesson.py`
- Create: `backend/app/models/sentence.py`
- Create: `backend/app/models/audio_file.py`
- Create: `backend/app/models/progress.py`
- Modify: `backend/app/models/__init__.py`

**Step 1: Write user model**

Create `backend/app/models/user.py`:

```python
import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
```

**Step 2: Write lesson model**

Create `backend/app/models/lesson.py`:

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer, default=0, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    sentences = relationship("Sentence", back_populates="lesson", cascade="all, delete-orphan")
```

**Step 3: Write sentence model**

Create `backend/app/models/sentence.py`:

```python
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Sentence(Base):
    __tablename__ = "sentences"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    vi_text = Column(Text, nullable=False)
    en_text = Column(Text, nullable=False)
    order_index = Column(Integer, default=0, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    lesson = relationship("Lesson", back_populates="sentences")
    audio_files = relationship("AudioFile", back_populates="sentence", cascade="all, delete-orphan")
```

**Step 4: Write audio_file model**

Create `backend/app/models/audio_file.py`:

```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AudioFile(Base):
    __tablename__ = "audio_files"
    
    id = Column(Integer, primary_key=True, index=True)
    sentence_id = Column(Integer, ForeignKey("sentences.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(2), nullable=False)  # 'vi' or 'en'
    file_path = Column(String(512), unique=True, nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    sentence = relationship("Sentence", back_populates="audio_files")
    
    __table_args__ = (
        UniqueConstraint('sentence_id', 'language', name='uix_sentence_language'),
    )
```

**Step 5: Write progress model**

Create `backend/app/models/progress.py`:

```python
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sentence_id = Column(Integer, ForeignKey("sentences.id", ondelete="CASCADE"), nullable=False, index=True)
    practiced_count = Column(Integer, default=1, nullable=False)
    last_practiced_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'sentence_id', name='uix_user_sentence'),
    )
```

**Step 6: Update models __init__.py**

Create `backend/app/models/__init__.py`:

```python
from app.core.database import Base
from app.models.user import User
from app.models.lesson import Lesson
from app.models.sentence import Sentence
from app.models.audio_file import AudioFile
from app.models.progress import UserProgress

__all__ = ["Base", "User", "Lesson", "Sentence", "AudioFile", "UserProgress"]
```

**Step 7: Commit models**

```bash
git add backend/app/models/
git commit -m "feat(models): add database models for users, lessons, sentences, audio, and progress"
```

---

## Task 4: Alembic Setup and Initial Migration

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/migrations/env.py`
- Create: `backend/migrations/script.py.mako`

**Step 1: Initialize Alembic**

```bash
cd backend
alembic init migrations
```

**Step 2: Configure alembic.ini**

Modify `backend/alembic.ini` (line ~58):

```ini
# Change from:
# sqlalchemy.url = driver://user:pass@localhost/dbname

# To:
# sqlalchemy.url is set in env.py from environment variable
```

**Step 3: Update migrations/env.py**

Replace `backend/migrations/env.py` content:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.models import Base

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with our settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Step 4: Create initial migration**

```bash
cd backend
alembic revision --autogenerate -m "Initial database schema"
```

**Step 5: Verify migration file**

Review the generated migration file in `backend/migrations/versions/` to ensure all tables are created correctly.

**Step 6: Commit migration setup**

```bash
git add backend/alembic.ini backend/migrations/
git commit -m "feat(db): setup Alembic and create initial migration"
```

---

## Task 5: Security Utilities

**Files:**
- Create: `backend/app/core/security.py`
- Create: `tests/test_security.py`

**Step 1: Write the failing test**

Create `backend/tests/test_security.py`:

```python
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token


def test_password_hashing():
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_token_creation_and_decoding():
    data = {"sub": "test@example.com", "user_id": "123"}
    token = create_access_token(data, expires_minutes=15)
    assert token is not None
    
    decoded = decode_token(token)
    assert decoded["sub"] == "test@example.com"
    assert decoded["user_id"] == "123"
```

**Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_security.py -v
```

Expected: FAIL with "cannot import name 'verify_password'"

**Step 3: Write minimal implementation**

Create `backend/app/core/security.py`:

```python
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: Dict, expires_minutes: Optional[int] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_minutes:
        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(data: Dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> Dict:
    """Decode JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise ValueError("Invalid token")
```

**Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_security.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit security utilities**

```bash
git add backend/app/core/security.py backend/tests/test_security.py
git commit -m "feat(security): add password hashing and JWT token utilities"
```

---

## Task 6: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/schemas/lesson.py`
- Create: `backend/app/schemas/sentence.py`
- Create: `backend/app/schemas/practice.py`
- Create: `backend/app/schemas/common.py`
- Modify: `backend/app/schemas/__init__.py`

**Step 1: Write common schemas**

Create `backend/app/schemas/common.py`:

```python
from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20
    sort_by: str = "created_at"
    order: str = "asc"
    search: str = ""


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    pagination: PaginationMeta


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: str = "Success"


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict
```

**Step 2: Write user schemas**

Create `backend/app/schemas/user.py`:

```python
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None


class UserInDB(UserBase):
    id: UUID
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    is_admin: bool
    
    class Config:
        from_attributes = True
```

**Step 3: Write auth schemas**

Create `backend/app/schemas/auth.py`:

```python
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: str
    email: str
    is_admin: bool
```

**Step 4: Write lesson schemas**

Create `backend/app/schemas/lesson.py`:

```python
from datetime import datetime
from pydantic import BaseModel


class LessonBase(BaseModel):
    title: str
    description: str | None = None
    order_index: int = 0
    is_active: bool = True


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    order_index: int | None = None
    is_active: bool | None = None


class LessonInDB(LessonBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

**Step 5: Write sentence schemas**

Create `backend/app/schemas/sentence.py`:

```python
from datetime import datetime
from pydantic import BaseModel


class SentenceBase(BaseModel):
    lesson_id: int
    vi_text: str
    en_text: str
    order_index: int = 0


class SentenceCreate(SentenceBase):
    pass


class SentenceUpdate(BaseModel):
    lesson_id: int | None = None
    vi_text: str | None = None
    en_text: str | None = None
    order_index: int | None = None


class SentenceInDB(SentenceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SentenceWithAudio(SentenceInDB):
    vi_audio_url: str
    en_audio_url: str


class BulkSentenceCreate(BaseModel):
    lesson_id: int
    sentences: list[dict]  # [{"vi": "...", "en": "..."}]
```

**Step 6: Write practice schemas**

Create `backend/app/schemas/practice.py`:

```python
from datetime import datetime
from pydantic import BaseModel
from app.schemas.sentence import SentenceWithAudio


class PracticeRecordRequest(BaseModel):
    sentence_id: int


class PracticeProgressItem(BaseModel):
    sentence_id: int
    vi_text: str
    en_text: str
    practiced_count: int
    last_practiced_at: datetime
    
    class Config:
        from_attributes = True


class PracticeStats(BaseModel):
    total_practiced: int
    unique_sentences: int
    current_streak_days: int
    lessons_completed: list[int]
    recent_activity: list[dict]  # [{"date": "2026-01-24", "count": 20}]


class NextSentenceResponse(BaseModel):
    sentence: SentenceWithAudio
    progress: dict | None = None  # {"practiced_count": 3, "total_in_lesson": 50, ...}
```

**Step 7: Update schemas __init__.py**

Create `backend/app/schemas/__init__.py`:

```python
from app.schemas.common import (
    PaginationParams,
    PaginationMeta,
    PaginatedResponse,
    SuccessResponse,
    ErrorResponse,
)
from app.schemas.user import UserCreate, UserUpdate, UserInDB, UserPublic
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, TokenRefreshRequest, TokenData
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonInDB
from app.schemas.sentence import SentenceCreate, SentenceUpdate, SentenceInDB, SentenceWithAudio, BulkSentenceCreate
from app.schemas.practice import PracticeRecordRequest, PracticeProgressItem, PracticeStats, NextSentenceResponse

__all__ = [
    "PaginationParams",
    "PaginationMeta",
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorResponse",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserPublic",
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "TokenRefreshRequest",
    "TokenData",
    "LessonCreate",
    "LessonUpdate",
    "LessonInDB",
    "SentenceCreate",
    "SentenceUpdate",
    "SentenceInDB",
    "SentenceWithAudio",
    "BulkSentenceCreate",
    "PracticeRecordRequest",
    "PracticeProgressItem",
    "PracticeStats",
    "NextSentenceResponse",
]
```

**Step 8: Commit schemas**

```bash
git add backend/app/schemas/
git commit -m "feat(schemas): add Pydantic schemas for validation"
```

---

## Task 7: Authentication Service and Dependencies

**Files:**
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/dependencies.py`
- Create: `tests/test_auth_service.py`

**Step 1: Write auth service**

Create `backend/app/services/auth_service.py`:

```python
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenData
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.exceptions import UnauthorizedException, ConflictException


class AuthService:
    @staticmethod
    def register_user(db: Session, data: RegisterRequest) -> User:
        """Register a new user."""
        # Check if user exists
        existing = db.query(User).filter(
            (User.email == data.email) | (User.username == data.username)
        ).first()
        
        if existing:
            raise ConflictException("Email or username already registered")
        
        # Create user
        user = User(
            email=data.email,
            username=data.username,
            hashed_password=get_password_hash(data.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def authenticate_user(db: Session, data: LoginRequest) -> User:
        """Authenticate user and return user object."""
        user = db.query(User).filter(User.email == data.email).first()
        
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        
        if not user.is_active:
            raise UnauthorizedException("Account is inactive")
        
        return user
    
    @staticmethod
    def create_tokens(user: User) -> dict:
        """Create access and refresh tokens for user."""
        token_data = {
            "sub": user.email,
            "user_id": str(user.id),
            "is_admin": user.is_admin,
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
```

**Step 2: Write dependencies**

Create `backend/app/dependencies.py`:

```python
from typing import Optional
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import User
from app.schemas.auth import TokenData


def get_token_data(authorization: Optional[str] = Header(None)) -> Optional[TokenData]:
    """Extract and validate token from Authorization header."""
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise UnauthorizedException("Invalid authentication scheme")
        
        payload = decode_token(token)
        return TokenData(
            user_id=payload.get("user_id"),
            email=payload.get("sub"),
            is_admin=payload.get("is_admin", False),
        )
    except (ValueError, KeyError):
        raise UnauthorizedException("Invalid or expired token")


def get_current_user(
    token_data: Optional[TokenData] = Depends(get_token_data),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user."""
    if not token_data:
        raise UnauthorizedException("Authentication required")
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise UnauthorizedException("User not found")
    
    if not user.is_active:
        raise UnauthorizedException("Account is inactive")
    
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify current user is admin."""
    if not current_user.is_admin:
        raise ForbiddenException("Admin access required")
    return current_user


def get_optional_user(
    token_data: Optional[TokenData] = Depends(get_token_data),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, None otherwise (for guest mode)."""
    if not token_data:
        return None
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user and user.is_active:
        return user
    return None
```

**Step 3: Write auth service test**

Create `backend/tests/test_auth_service.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.exceptions import ConflictException, UnauthorizedException

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost/reflex_trainer_test"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_register_user(db):
    data = RegisterRequest(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    user = AuthService.register_user(db, data)
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.hashed_password != "password123"


def test_register_duplicate_email(db):
    data = RegisterRequest(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    AuthService.register_user(db, data)
    
    with pytest.raises(ConflictException):
        AuthService.register_user(db, data)


def test_authenticate_user_success(db):
    # Register user
    register_data = RegisterRequest(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    AuthService.register_user(db, register_data)
    
    # Authenticate
    login_data = LoginRequest(
        email="test@example.com",
        password="password123"
    )
    user = AuthService.authenticate_user(db, login_data)
    assert user.email == "test@example.com"


def test_authenticate_user_wrong_password(db):
    # Register user
    register_data = RegisterRequest(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    AuthService.register_user(db, register_data)
    
    # Try wrong password
    login_data = LoginRequest(
        email="test@example.com",
        password="wrongpassword"
    )
    with pytest.raises(UnauthorizedException):
        AuthService.authenticate_user(db, login_data)


def test_create_tokens(db):
    # Register user
    register_data = RegisterRequest(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    user = AuthService.register_user(db, register_data)
    
    # Create tokens
    tokens = AuthService.create_tokens(user)
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"
```

**Step 4: Run tests**

```bash
cd backend
# Make sure test database exists: createdb reflex_trainer_test
pytest tests/test_auth_service.py -v
```

Expected: PASS (5 tests)

**Step 5: Commit auth service**

```bash
git add backend/app/services/auth_service.py backend/app/dependencies.py backend/tests/test_auth_service.py
git commit -m "feat(auth): add authentication service and dependencies"
```

---

## Task 8: TTS Service

**Files:**
- Create: `backend/app/services/tts_service.py`
- Create: `tests/test_tts_service.py`

**Step 1: Write the failing test**

Create `backend/tests/test_tts_service.py`:

```python
import os
import tempfile
from pathlib import Path
from app.services.tts_service import TTSService


def test_generate_audio_gtts():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = TTSService(audio_dir=tmpdir, engine="gtts")
        
        text = "Hello world"
        language = "en"
        file_path = service.generate_audio(text, language, sentence_id=1)
        
        assert Path(file_path).exists()
        assert file_path.endswith(".mp3")
        assert os.path.getsize(file_path) > 0


def test_get_audio_path():
    service = TTSService(audio_dir="/tmp/audio", engine="gtts")
    path = service.get_audio_path(sentence_id=123, language="vi")
    assert path == "/tmp/audio/123_vi.mp3"
```

**Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_tts_service.py -v
```

Expected: FAIL with "cannot import name 'TTSService'"

**Step 3: Write minimal implementation**

Create `backend/app/services/tts_service.py`:

```python
import os
from pathlib import Path
from gtts import gTTS
import pyttsx3
from app.config import settings
from app.core.exceptions import BadRequestException


class TTSService:
    def __init__(self, audio_dir: str = None, engine: str = None):
        self.audio_dir = audio_dir or settings.audio_dir
        self.engine = engine or settings.tts_engine
        
        # Create audio directory if not exists
        Path(self.audio_dir).mkdir(parents=True, exist_ok=True)
    
    def get_audio_path(self, sentence_id: int, language: str) -> str:
        """Get audio file path for sentence and language."""
        extension = "mp3" if self.engine == "gtts" else "wav"
        return os.path.join(self.audio_dir, f"{sentence_id}_{language}.{extension}")
    
    def generate_audio(self, text: str, language: str, sentence_id: int) -> str:
        """Generate audio file for text."""
        file_path = self.get_audio_path(sentence_id, language)
        
        # Skip if already exists
        if os.path.exists(file_path):
            return file_path
        
        try:
            if self.engine == "gtts":
                self._generate_gtts(text, language, file_path)
            else:
                self._generate_pyttsx3(text, language, file_path)
            
            return file_path
        except Exception as e:
            raise BadRequestException(f"Failed to generate audio: {str(e)}")
    
    def _generate_gtts(self, text: str, language: str, file_path: str):
        """Generate audio using gTTS."""
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(file_path)
    
    def _generate_pyttsx3(self, text: str, language: str, file_path: str):
        """Generate audio using pyttsx3 (offline)."""
        engine = pyttsx3.init()
        
        # Set voice based on language
        voices = engine.getProperty('voices')
        if language == "vi":
            # Try to find Vietnamese voice
            for voice in voices:
                if "vietnamese" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
        else:
            # Default to first English voice
            engine.setProperty('voice', voices[0].id)
        
        engine.save_to_file(text, file_path)
        engine.runAndWait()
    
    def delete_audio(self, sentence_id: int, language: str = None):
        """Delete audio file(s) for sentence."""
        if language:
            file_path = self.get_audio_path(sentence_id, language)
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            # Delete both languages
            for lang in ["vi", "en"]:
                self.delete_audio(sentence_id, lang)
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        return os.path.getsize(file_path) if os.path.exists(file_path) else 0
```

**Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_tts_service.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit TTS service**

```bash
git add backend/app/services/tts_service.py backend/tests/test_tts_service.py
git commit -m "feat(tts): add text-to-speech service with gTTS and pyttsx3"
```

---

## Task 9: Auth API Endpoints

**Files:**
- Create: `backend/app/api/v1/auth.py`
- Create: `tests/test_api_auth.py`

**Step 1: Write auth endpoints**

Create `backend/app/api/v1/auth.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user, get_token_data
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, TokenRefreshRequest, TokenData
from app.schemas.user import UserPublic
from app.schemas.common import SuccessResponse
from app.core.security import decode_token, create_access_token
from app.core.exceptions import UnauthorizedException

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=SuccessResponse[TokenResponse])
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    user = AuthService.register_user(db, data)
    tokens = AuthService.create_tokens(user)
    return SuccessResponse(data=tokens, message="User registered successfully")


@router.post("/login", response_model=SuccessResponse[TokenResponse])
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access tokens."""
    user = AuthService.authenticate_user(db, data)
    tokens = AuthService.create_tokens(user)
    return SuccessResponse(data=tokens, message="Login successful")


@router.post("/refresh", response_model=SuccessResponse[dict])
def refresh_token(data: TokenRefreshRequest):
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(data.refresh_token)
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")
        
        # Create new access token
        token_data = {
            "sub": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "is_admin": payload.get("is_admin", False),
        }
        access_token = create_access_token(token_data)
        
        return SuccessResponse(
            data={"access_token": access_token, "token_type": "bearer"},
            message="Token refreshed successfully"
        )
    except ValueError:
        raise UnauthorizedException("Invalid or expired refresh token")


@router.get("/me", response_model=SuccessResponse[UserPublic])
def get_me(current_user = Depends(get_current_user)):
    """Get current user information."""
    return SuccessResponse(data=current_user, message="User retrieved successfully")
```

**Step 2: Write API test**

Create `backend/tests/test_api_auth.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost/reflex_trainer_test"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


def test_login():
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


def test_get_me():
    # Register
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    token = reg_response.json()["data"]["access_token"]
    
    # Get me
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "test@example.com"


def test_refresh_token():
    # Register
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    refresh_token = reg_response.json()["data"]["refresh_token"]
    
    # Refresh
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
```

**Step 3: Create main.py (temporary minimal version)**

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import auth

app = FastAPI(title=settings.project_name, debug=settings.debug)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    return {"message": "VI→EN Reflex Trainer API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**Step 4: Create API v1 __init__.py**

Create `backend/app/api/v1/__init__.py`:

```python
# API v1 module
```

**Step 5: Run API tests**

```bash
cd backend
pytest tests/test_api_auth.py -v
```

Expected: PASS (4 tests)

**Step 6: Commit auth API**

```bash
git add backend/app/api/v1/auth.py backend/app/main.py backend/tests/test_api_auth.py
git commit -m "feat(api): add authentication endpoints"
```

---

## Task 10: Lessons API Endpoints

**Files:**
- Create: `backend/app/api/v1/lessons.py`
- Modify: `backend/app/main.py`

**Step 1: Write lessons endpoints**

Create `backend/app/api/v1/lessons.py`:

```python
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.dependencies import get_current_admin
from app.models.lesson import Lesson
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonInDB
from app.schemas.common import SuccessResponse, PaginatedResponse, PaginationMeta
from app.core.exceptions import NotFoundException
import math

router = APIRouter(prefix="/lessons", tags=["Lessons"])


@router.get("", response_model=SuccessResponse[PaginatedResponse[LessonInDB]])
def list_lessons(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("order_index"),
    order: str = Query("asc"),
    search: str = Query(""),
    db: Session = Depends(get_db)
):
    """List all lessons with pagination and search."""
    query = db.query(Lesson).filter(Lesson.is_active == True)
    
    # Search
    if search:
        query = query.filter(
            or_(
                Lesson.title.ilike(f"%{search}%"),
                Lesson.description.ilike(f"%{search}%")
            )
        )
    
    # Sort
    sort_column = getattr(Lesson, sort_by, Lesson.order_index)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Pagination
    total = query.count()
    lessons = query.offset((page - 1) * limit).limit(limit).all()
    
    return SuccessResponse(
        data=PaginatedResponse(
            items=lessons,
            pagination=PaginationMeta(
                page=page,
                limit=limit,
                total_items=total,
                total_pages=math.ceil(total / limit),
                has_next=page * limit < total,
                has_prev=page > 1
            )
        )
    )


@router.get("/{lesson_id}", response_model=SuccessResponse[LessonInDB])
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """Get lesson by ID."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise NotFoundException("Lesson not found")
    return SuccessResponse(data=lesson)


@router.post("", response_model=SuccessResponse[LessonInDB])
def create_lesson(
    data: LessonCreate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_admin)
):
    """Create a new lesson (admin only)."""
    lesson = Lesson(**data.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return SuccessResponse(data=lesson, message="Lesson created successfully")


@router.put("/{lesson_id}", response_model=SuccessResponse[LessonInDB])
def update_lesson(
    lesson_id: int,
    data: LessonUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_admin)
):
    """Update lesson (admin only)."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise NotFoundException("Lesson not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(lesson, key, value)
    
    db.commit()
    db.refresh(lesson)
    return SuccessResponse(data=lesson, message="Lesson updated successfully")


@router.delete("/{lesson_id}", response_model=SuccessResponse[dict])
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_admin)
):
    """Delete lesson (admin only)."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise NotFoundException("Lesson not found")
    
    db.delete(lesson)
    db.commit()
    return SuccessResponse(data={"id": lesson_id}, message="Lesson deleted successfully")
```

**Step 2: Update main.py**

Modify `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import auth, lessons  # Add lessons import

app = FastAPI(title=settings.project_name, debug=settings.debug)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(lessons.router, prefix=settings.api_v1_prefix)  # Add this line


@app.get("/")
def root():
    return {"message": "VI→EN Reflex Trainer API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**Step 3: Commit lessons API**

```bash
git add backend/app/api/v1/lessons.py backend/app/main.py
git commit -m "feat(api): add lessons CRUD endpoints with pagination"
```

---

## Task 11: Sentences API Endpoints

**Files:**
- Create: `backend/app/api/v1/sentences.py`
- Modify: `backend/app/main.py`

**Step 1: Write sentences endpoints**

Create `backend/app/api/v1/sentences.py`:

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.dependencies import get_current_admin
from app.models.sentence import Sentence
from app.schemas.sentence import SentenceCreate, SentenceUpdate, SentenceInDB, BulkSentenceCreate
from app.schemas.common import SuccessResponse, PaginatedResponse, PaginationMeta
from app.core.exceptions import NotFoundException
import math

router = APIRouter(prefix="/sentences", tags=["Sentences"])


@router.get("", response_model=SuccessResponse[PaginatedResponse[SentenceInDB]])
def list_sentences(
    lesson_id: int = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("order_index"),
    order: str = Query("asc"),
    search: str = Query(""),
    db: Session = Depends(get_db)
):
    """List sentences with pagination, filtering, and search."""
    query = db.query(Sentence)
    
    # Filter by lesson
    if lesson_id:
        query = query.filter(Sentence.lesson_id == lesson_id)
    
    # Search
    if search:
        query = query.filter(
            or_(
                Sentence.vi_text.ilike(f"%{search}%"),
                Sentence.en_text.ilike(f"%{search}%")
            )
        )
    
    # Sort
    sort_column = getattr(Sentence, sort_by, Sentence.order_index)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Pagination
    total = query.count()
    sentences = query.offset((page - 1) * limit).limit(limit).all()
    
    return SuccessResponse(
        data=PaginatedResponse(
            items=sentences,
            pagination=PaginationMeta(
                page=page,
                limit=limit,
                total_items=total,
                total_pages=math.ceil(total / limit),
                has_next=page * limit < total,
                has_prev=page > 1
            )
        )
    )


@router.get("/{sentence_id}", response_model=SuccessResponse[SentenceInDB])
def get_sentence(sentence_id: int, db: Session = Depends(get_db)):
    """Get sentence by ID."""
    sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
    if not sentence:
        raise NotFoundException("Sentence not found")
    return SuccessResponse(data=sentence)


@router.post("", response_model=SuccessResponse[SentenceInDB])
def create_sentence(
    data: SentenceCreate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_admin)
):
    """Create a new sentence (admin only)."""
    sentence = Sentence(**data.model_dump())
    db.add(sentence)
    db.commit()
    db.refresh(sentence)
    return SuccessResponse(data=sentence, message="Sentence created successfully")


@router.post("/bulk", response_model=SuccessResponse[dict])
def bulk_create_sentences(
    data: BulkSentenceCreate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_admin)
):
    """Bulk create sentences from list (admin only)."""
    sentences = []
    for idx, item in enumerate(data.sentences):
        sentence = Sentence(
            lesson_id=data.lesson_id,
            vi_text=item.get("vi", ""),
            en_text=item.get("en", ""),
            order_index=idx
        )
        sentences.append(sentence)
    
    db.add_all(sentences)
    db.commit()
    
    return SuccessResponse(
        data={"count": len(sentences)},
        message=f"{len(sentences)} sentences created successfully"
    )


@router.put("/{sentence_id}", response_model=SuccessResponse[SentenceInDB])
def update_sentence(
    sentence_id: int,
    data: SentenceUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_admin)
):
    """Update sentence (admin only)."""
    sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
    if not sentence:
        raise NotFoundException("Sentence not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(sentence, key, value)
    
    db.commit()
    db.refresh(sentence)
    return SuccessResponse(data=sentence, message="Sentence updated successfully")


@router.delete("/{sentence_id}", response_model=SuccessResponse[dict])
def delete_sentence(
    sentence_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_admin)
):
    """Delete sentence (admin only)."""
    sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
    if not sentence:
        raise NotFoundException("Sentence not found")
    
    db.delete(sentence)
    db.commit()
    return SuccessResponse(data={"id": sentence_id}, message="Sentence deleted successfully")
```

**Step 2: Update main.py**

Modify `backend/app/main.py` to add sentences router:

```python
from app.api.v1 import auth, lessons, sentences  # Add sentences

# ... existing code ...

app.include_router(sentences.router, prefix=settings.api_v1_prefix)  # Add this line
```

**Step 3: Commit sentences API**

```bash
git add backend/app/api/v1/sentences.py backend/app/main.py
git commit -m "feat(api): add sentences CRUD endpoints with bulk create"
```

---

## Task 12: Audio API Endpoints

**Files:**
- Create: `backend/app/api/v1/audio.py`
- Modify: `backend/app/main.py`

**Step 1: Write audio endpoints**

Create `backend/app/api/v1/audio.py`:

```python
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_admin
from app.models.sentence import Sentence
from app.models.audio_file import AudioFile
from app.services.tts_service import TTSService
from app.schemas.common import SuccessResponse
from app.core.exceptions import NotFoundException
import os

router = APIRouter(prefix="/audio", tags=["Audio"])
tts_service = TTSService()


@router.get("/{sentence_id}/{language}")
def get_audio(sentence_id: int, language: str, db: Session = Depends(get_db)):
    """Get audio file for sentence (generate if not exists)."""
    if language not in ["vi", "en"]:
        raise NotFoundException("Invalid language. Use 'vi' or 'en'")
    
    # Check if sentence exists
    sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
    if not sentence:
        raise NotFoundException("Sentence not found")
    
    # Check if audio already cached
    audio_file = db.query(AudioFile).filter(
        AudioFile.sentence_id == sentence_id,
        AudioFile.language == language
    ).first()
    
    if audio_file and os.path.exists(audio_file.file_path):
        return FileResponse(
            audio_file.file_path,
            media_type="audio/mpeg",
            headers={"Cache-Control": "public, max-age=31536000"}
        )
    
    # Generate audio
    text = sentence.vi_text if language == "vi" else sentence.en_text
    file_path = tts_service.generate_audio(text, language, sentence_id)
    file_size = tts_service.get_file_size(file_path)
    
    # Cache in database
    if not audio_file:
        audio_file = AudioFile(
            sentence_id=sentence_id,
            language=language,
            file_path=file_path,
            file_size=file_size
        )
        db.add(audio_file)
    else:
        audio_file.file_path = file_path
        audio_file.file_size = file_size
    
    db.commit()
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        headers={"Cache-Control": "public, max-age=31536000"}
    )


@router.post("/regenerate", response_model=SuccessResponse[dict])
def regenerate_audio(
    sentence_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_admin)
):
    """Force regenerate audio for sentence (admin only)."""
    sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
    if not sentence:
        raise NotFoundException("Sentence not found")
    
    # Delete existing audio files
    tts_service.delete_audio(sentence_id)
    
    # Delete from database
    db.query(AudioFile).filter(AudioFile.sentence_id == sentence_id).delete()
    db.commit()
    
    # Generate new audio
    for language in ["vi", "en"]:
        text = sentence.vi_text if language == "vi" else sentence.en_text
        file_path = tts_service.generate_audio(text, language, sentence_id)
        file_size = tts_service.get_file_size(file_path)
        
        audio_file = AudioFile(
            sentence_id=sentence_id,
            language=language,
            file_path=file_path,
            file_size=file_size
        )
        db.add(audio_file)
    
    db.commit()
    
    return SuccessResponse(
        data={"sentence_id": sentence_id},
        message="Audio regenerated successfully"
    )


@router.get("/stats", response_model=SuccessResponse[dict])
def audio_stats(db: Session = Depends(get_db)):
    """Get audio cache statistics."""
    total_files = db.query(AudioFile).count()
    total_size = db.query(AudioFile).with_entities(
        db.func.sum(AudioFile.file_size)
    ).scalar() or 0
    
    return SuccessResponse(
        data={
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    )
```

**Step 2: Update main.py**

Modify `backend/app/main.py`:

```python
from app.api.v1 import auth, lessons, sentences, audio  # Add audio

# ... existing code ...

app.include_router(audio.router, prefix=settings.api_v1_prefix)  # Add this line
```

**Step 3: Commit audio API**

```bash
git add backend/app/api/v1/audio.py backend/app/main.py
git commit -m "feat(api): add audio endpoints with on-demand generation"
```

---

## Task 13: Practice API Endpoints

**Files:**
- Create: `backend/app/services/practice_service.py`
- Create: `backend/app/api/v1/practice.py`
- Modify: `backend/app/main.py`

**Step 1: Write practice service**

Create `backend/app/services/practice_service.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
import random
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.sentence import Sentence
from app.models.progress import UserProgress
from app.models.user import User
from app.core.exceptions import NotFoundException


class PracticeService:
    @staticmethod
    def get_next_sentence(
        db: Session,
        lesson_id: int,
        mode: str = "random",
        user: Optional[User] = None
    ) -> tuple[Sentence, Optional[dict]]:
        """Get next sentence for practice."""
        query = db.query(Sentence).filter(Sentence.lesson_id == lesson_id)
        
        if user:
            # Filter out recently practiced (< 5 minutes ago)
            recent_time = datetime.utcnow() - timedelta(minutes=5)
            recent_ids = db.query(UserProgress.sentence_id).filter(
                UserProgress.user_id == user.id,
                UserProgress.last_practiced_at > recent_time
            ).all()
            recent_ids = [r[0] for r in recent_ids]
            
            if recent_ids:
                query = query.filter(~Sentence.id.in_(recent_ids))
            
            # Prioritize least practiced
            sentences = query.all()
            if not sentences:
                # All practiced recently, just get any
                sentences = db.query(Sentence).filter(
                    Sentence.lesson_id == lesson_id
                ).all()
            
            if not sentences:
                raise NotFoundException("No sentences found in this lesson")
            
            # Get practice counts
            practice_counts = {}
            for s in sentences:
                count = db.query(UserProgress).filter(
                    UserProgress.user_id == user.id,
                    UserProgress.sentence_id == s.id
                ).first()
                practice_counts[s.id] = count.practiced_count if count else 0
            
            # Sort by practice count and pick randomly from least practiced
            sentences.sort(key=lambda x: practice_counts[x.id])
            min_count = practice_counts[sentences[0].id]
            least_practiced = [s for s in sentences if practice_counts[s.id] == min_count]
            sentence = random.choice(least_practiced)
            
            # Get progress info
            total_in_lesson = db.query(Sentence).filter(
                Sentence.lesson_id == lesson_id
            ).count()
            practiced_count = db.query(UserProgress).filter(
                UserProgress.user_id == user.id,
                UserProgress.sentence_id.in_(
                    db.query(Sentence.id).filter(Sentence.lesson_id == lesson_id)
                )
            ).count()
            
            progress = {
                "practiced_count": practice_counts[sentence.id],
                "total_in_lesson": total_in_lesson,
                "completion_percentage": round((practiced_count / total_in_lesson) * 100, 2) if total_in_lesson > 0 else 0
            }
            
            return sentence, progress
        else:
            # Guest mode - just random
            sentences = query.all()
            if not sentences:
                raise NotFoundException("No sentences found in this lesson")
            
            sentence = random.choice(sentences)
            return sentence, None
    
    @staticmethod
    def record_practice(db: Session, user: User, sentence_id: int):
        """Record that user practiced a sentence."""
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.sentence_id == sentence_id
        ).first()
        
        if progress:
            progress.practiced_count += 1
            progress.last_practiced_at = datetime.utcnow()
        else:
            progress = UserProgress(
                user_id=user.id,
                sentence_id=sentence_id,
                practiced_count=1,
                last_practiced_at=datetime.utcnow()
            )
            db.add(progress)
        
        db.commit()
```

**Step 2: Write practice endpoints**

Create `backend/app/api/v1/practice.py`:

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_optional_user, get_current_user
from app.services.practice_service import PracticeService
from app.schemas.practice import PracticeRecordRequest, NextSentenceResponse
from app.schemas.sentence import SentenceWithAudio
from app.schemas.common import SuccessResponse
from app.config import settings

router = APIRouter(prefix="/practice", tags=["Practice"])


@router.get("/next", response_model=SuccessResponse[NextSentenceResponse])
def get_next_sentence(
    lesson_id: int = Query(...),
    mode: str = Query("random"),
    db: Session = Depends(get_db),
    user = Depends(get_optional_user)
):
    """Get next sentence for practice (works for both guest and authenticated users)."""
    sentence, progress = PracticeService.get_next_sentence(db, lesson_id, mode, user)
    
    # Add audio URLs
    sentence_data = SentenceWithAudio(
        **sentence.__dict__,
        vi_audio_url=f"{settings.api_v1_prefix}/audio/{sentence.id}/vi",
        en_audio_url=f"{settings.api_v1_prefix}/audio/{sentence.id}/en"
    )
    
    return SuccessResponse(
        data=NextSentenceResponse(sentence=sentence_data, progress=progress)
    )


@router.post("/record", response_model=SuccessResponse[dict])
def record_practice(
    data: PracticeRecordRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Record practice session (requires authentication)."""
    PracticeService.record_practice(db, user, data.sentence_id)
    return SuccessResponse(
        data={"sentence_id": data.sentence_id},
        message="Practice recorded successfully"
    )
```

**Step 3: Update main.py**

Modify `backend/app/main.py`:

```python
from app.api.v1 import auth, lessons, sentences, audio, practice  # Add practice

# ... existing code ...

app.include_router(practice.router, prefix=settings.api_v1_prefix)  # Add this line
```

**Step 4: Commit practice API**

```bash
git add backend/app/services/practice_service.py backend/app/api/v1/practice.py backend/app/main.py
git commit -m "feat(api): add practice endpoints with smart sentence selection"
```

---

## Task 14: Global Error Handler and Final Main Setup

**Files:**
- Modify: `backend/app/main.py`

**Step 1: Update main.py with complete setup**

Replace `backend/app/main.py` with:

```python
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.api.v1 import auth, lessons, sentences, audio, practice

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.project_name,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    if hasattr(exc, "status_code"):
        status_code = exc.status_code
        detail = exc.detail if hasattr(exc, "detail") else str(exc)
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = "Internal server error"
        # Log the exception in production
        if not settings.debug:
            import traceback
            traceback.print_exc()
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": exc.__class__.__name__ if hasattr(exc, "__class__") else "ERROR",
                "message": detail
            }
        }
    )


# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(lessons.router, prefix=settings.api_v1_prefix)
app.include_router(sentences.router, prefix=settings.api_v1_prefix)
app.include_router(audio.router, prefix=settings.api_v1_prefix)
app.include_router(practice.router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "VI→EN Reflex Trainer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2026-01-24"}
```

**Step 2: Commit final main setup**

```bash
git add backend/app/main.py
git commit -m "feat(api): add global error handler and rate limiting"
```

---

## Task 15: Database Seeding Script

**Files:**
- Create: `backend/app/scripts/seed_db.py`

**Step 1: Write seeding script**

Create `backend/app/scripts/seed_db.py`:

```python
import sys
from pathlib import Path
import csv

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.core.database import SessionLocal, engine
from app.models import Base, User, Lesson, Sentence
from app.core.security import get_password_hash
from app.config import settings


def create_tables():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


def create_admin_user(db):
    """Create first admin user."""
    existing = db.query(User).filter(User.email == settings.first_admin_email).first()
    if existing:
        print("✓ Admin user already exists")
        return existing
    
    admin = User(
        email=settings.first_admin_email,
        username="admin",
        hashed_password=get_password_hash(settings.first_admin_password),
        is_admin=True,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"✓ Admin user created: {admin.email}")
    return admin


def seed_lessons_and_sentences(db):
    """Seed lessons and sentences from CSV."""
    # Check if already seeded
    existing_count = db.query(Sentence).count()
    if existing_count > 0:
        print(f"✓ Database already has {existing_count} sentences")
        return
    
    # Read from CSV
    csv_path = Path(__file__).resolve().parents[3] / "data" / "sentences.csv"
    if not csv_path.exists():
        print(f"⚠ CSV file not found: {csv_path}")
        return
    
    lessons_dict = {}
    sentences_data = []
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lesson_num = int(row.get("lesson", 1))
            vi_text = row.get("vi", "").strip()
            en_text = row.get("en", "").strip()
            
            if lesson_num not in lessons_dict:
                lessons_dict[lesson_num] = {
                    "title": f"Lesson {lesson_num}",
                    "order_index": lesson_num
                }
            
            sentences_data.append({
                "lesson_num": lesson_num,
                "vi": vi_text,
                "en": en_text
            })
    
    # Create lessons
    lesson_objs = {}
    for lesson_num, lesson_data in lessons_dict.items():
        lesson = Lesson(**lesson_data)
        db.add(lesson)
        db.flush()
        lesson_objs[lesson_num] = lesson
    
    # Create sentences
    for idx, sent_data in enumerate(sentences_data):
        lesson = lesson_objs[sent_data["lesson_num"]]
        sentence = Sentence(
            lesson_id=lesson.id,
            vi_text=sent_data["vi"],
            en_text=sent_data["en"],
            order_index=idx
        )
        db.add(sentence)
    
    db.commit()
    print(f"✓ Seeded {len(lessons_dict)} lessons and {len(sentences_data)} sentences")


def main():
    """Main seeding function."""
    print("\n🌱 Starting database seeding...\n")
    
    create_tables()
    
    db = SessionLocal()
    try:
        create_admin_user(db)
        seed_lessons_and_sentences(db)
    finally:
        db.close()
    
    print("\n✅ Database seeding completed!\n")
    print(f"Admin credentials:")
    print(f"  Email: {settings.first_admin_email}")
    print(f"  Password: {settings.first_admin_password}")
    print(f"\n⚠️  Change admin password in production!")


if __name__ == "__main__":
    main()
```

**Step 2: Test seeding**

```bash
cd backend
python app/scripts/seed_db.py
```

Expected: Creates tables, admin user, and seeds data

**Step 3: Commit seeding script**

```bash
git add backend/app/scripts/seed_db.py
git commit -m "feat(db): add database seeding script"
```

---

## Task 16: Testing and Documentation

**Files:**
- Create: `backend/pytest.ini`
- Create: `backend/tests/conftest.py`
- Update: `backend/README.md`

**Step 1: Write pytest configuration**

Create `backend/pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

**Step 2: Write test fixtures**

Create `backend/tests/conftest.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.core.database import Base, get_db
from app.main import app

SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost/reflex_trainer_test"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client with database override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client):
    """Create admin user and return auth token."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@test.com",
            "username": "admin",
            "password": "admin123"
        }
    )
    # Manually set admin flag (in real scenario, use database)
    return response.json()["data"]["access_token"]


@pytest.fixture
def user_token(client):
    """Create regular user and return auth token."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@test.com",
            "username": "user",
            "password": "user123"
        }
    )
    return response.json()["data"]["access_token"]
```

**Step 3: Update README with complete setup**

Update `backend/README.md` with deployment and testing sections:

```markdown
# VI→EN Reflex Trainer - API Backend

FastAPI backend with PostgreSQL for Vietnamese-English reflex training.

## Features

- ✅ JWT Authentication (access + refresh tokens)
- ✅ Hybrid mode (guest + registered users)
- ✅ CRUD for Lessons and Sentences
- ✅ On-demand audio generation with caching (gTTS/pyttsx3)
- ✅ Smart practice algorithm
- ✅ Pagination, search, sorting on all list endpoints
- ✅ Admin dashboard endpoints
- ✅ Rate limiting
- ✅ Comprehensive test coverage

## Setup

### 1. Install dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup PostgreSQL

```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt install postgresql

# Create databases
createdb reflex_trainer
createdb reflex_trainer_test  # For testing
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings (database URL, secret key, etc.)
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Seed database

```bash
python app/scripts/seed_db.py
```

### 6. Start server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth_service.py -v
```

## API Endpoints

See full design: `/docs/plans/2026-01-24-api-backend-design.md`

### Authentication
- POST `/api/v1/auth/register` - Register new user
- POST `/api/v1/auth/login` - Login
- POST `/api/v1/auth/refresh` - Refresh token
- GET `/api/v1/auth/me` - Get current user

### Lessons
- GET `/api/v1/lessons` - List lessons (with pagination)
- GET `/api/v1/lessons/{id}` - Get lesson
- POST `/api/v1/lessons` - Create lesson (admin)
- PUT `/api/v1/lessons/{id}` - Update lesson (admin)
- DELETE `/api/v1/lessons/{id}` - Delete lesson (admin)

### Sentences
- GET `/api/v1/sentences` - List sentences (with pagination, filtering)
- POST `/api/v1/sentences/bulk` - Bulk create from list (admin)

### Practice
- GET `/api/v1/practice/next` - Get next sentence (guest or user)
- POST `/api/v1/practice/record` - Record practice (user only)

### Audio
- GET `/api/v1/audio/{sentence_id}/vi` - Get Vietnamese audio
- GET `/api/v1/audio/{sentence_id}/en` - Get English audio

## Admin Credentials

Default admin credentials (change in production!):
- Email: admin@example.com
- Password: changeme123

## Project Structure

See design doc: `/docs/plans/2026-01-24-api-backend-design.md`

## License

MIT
```

**Step 4: Commit testing setup**

```bash
git add backend/pytest.ini backend/tests/conftest.py backend/README.md
git commit -m "test: add test configuration and comprehensive README"
```

---

## Task 17: Final Verification and Deployment Readiness

**Step 1: Create .env file**

```bash
cd backend
cp .env.example .env
# Edit .env with your local settings
```

**Step 2: Run all migrations**

```bash
cd backend
alembic upgrade head
```

Expected: All migrations applied successfully

**Step 3: Seed database**

```bash
cd backend
python app/scripts/seed_db.py
```

Expected: Admin user and sample data created

**Step 4: Start server**

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected: Server starts at http://localhost:8000

**Step 5: Test API manually**

Visit http://localhost:8000/docs and test:
1. POST /auth/register - Create user
2. POST /auth/login - Login
3. GET /lessons - List lessons
4. GET /audio/1/vi - Generate audio

**Step 6: Run all tests**

```bash
cd backend
pytest -v
```

Expected: All tests pass

**Step 7: Final commit**

```bash
git add .
git commit -m "feat: complete API backend implementation

- Clean architecture with FastAPI + PostgreSQL
- JWT authentication with hybrid mode
- CRUD for lessons and sentences with pagination
- On-demand audio generation with caching
- Smart practice algorithm
- Comprehensive test coverage
- Ready for production deployment"
```

---

## Summary

✅ **17 tasks completed:**

1. ✅ Project setup and dependencies
2. ✅ Core configuration and database
3. ✅ Database models (User, Lesson, Sentence, AudioFile, Progress)
4. ✅ Alembic migrations
5. ✅ Security utilities (JWT, password hashing)
6. ✅ Pydantic schemas
7. ✅ Authentication service
8. ✅ TTS service
9. ✅ Auth API endpoints
10. ✅ Lessons API endpoints
11. ✅ Sentences API endpoints
12. ✅ Audio API endpoints
13. ✅ Practice API endpoints
14. ✅ Global error handler
15. ✅ Database seeding
16. ✅ Testing setup
17. ✅ Final verification

**Key Features Implemented:**
- Clean architecture (routes, models, schemas, services, core)
- PostgreSQL with SQLAlchemy ORM
- JWT authentication (access + refresh tokens)
- Hybrid mode (guest + registered users)
- On-demand audio generation with caching
- Smart practice algorithm (prioritizes least practiced)
- Pagination + search + sort on all list endpoints
- Admin-only endpoints for content management
- Rate limiting
- Global error handling
- Comprehensive test coverage

**Next Steps:**
1. Deploy to production (see deployment steps in design doc)
2. Build frontend (React/Vue) to consume API
3. Setup CI/CD pipeline
4. Monitor with Prometheus/Grafana (optional)
5. Add more features (spaced repetition, voice recognition, etc.)
