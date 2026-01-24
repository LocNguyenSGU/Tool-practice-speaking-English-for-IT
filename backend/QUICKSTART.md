# 🚀 Quick Start Guide - Chạy API dưới Local

Hướng dẫn chi tiết để chạy API backend trên máy local.

---

## ⚡ Cài đặt nhanh (< 5 phút)

### Bước 1: Chạy setup script

```bash
cd backend
chmod +x setup.sh run.sh
./setup.sh
```

Script sẽ tự động:
- ✅ Kiểm tra Python 3
- ✅ Tạo virtual environment
- ✅ Cài đặt dependencies
- ✅ Cấu hình database (PostgreSQL hoặc SQLite)
- ✅ Chạy migrations
- ✅ Seed dữ liệu mẫu

### Bước 2: Chạy server

```bash
./run.sh
```

✨ **Xong!** API đã chạy tại:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

---

## 📋 Cài đặt thủ công (Chi tiết)

### 1️⃣ Yêu cầu hệ thống

#### Cần thiết:
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **pip** (đi kèm Python)

#### Tùy chọn:
- **PostgreSQL 14+** (production, [Download](https://www.postgresql.org/download/))
- **SQLite** (development, có sẵn trong Python)

---

### 2️⃣ Clone & Navigate

```bash
cd vi-en-reflex-trainer/backend
```

---

### 3️⃣ Tạo Virtual Environment

```bash
# Tạo venv
python3 -m venv venv

# Kích hoạt venv
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verify
which python  # Should show path to venv/bin/python
```

---

### 4️⃣ Cài đặt Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install packages
pip install -r requirements.txt

# Verify
pip list
```

**Packages chính**:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `psycopg2-binary` - PostgreSQL driver
- `alembic` - Migrations
- `python-jose` - JWT
- `passlib` - Password hashing
- `gtts` - Text-to-speech
- `pytest` - Testing

---

### 5️⃣ Cấu hình Database

#### Option A: PostgreSQL (Recommended cho production)

**1. Cài đặt PostgreSQL:**

```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# Windows
# Download installer: https://www.postgresql.org/download/windows/
```

**2. Tạo database:**

```bash
# Mặc định user là 'postgres'
createdb reflex_trainer

# Hoặc với user khác
createdb -U your_username reflex_trainer

# Verify
psql -l | grep reflex_trainer
```

**3. Cấu hình .env:**

```bash
cp .env.example .env
nano .env  # hoặc vim, code, v.v.
```

Sửa dòng `DATABASE_URL`:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/reflex_trainer
```

#### Option B: SQLite (Nhanh cho development)

```bash
cp .env.example .env
nano .env
```

Sửa dòng `DATABASE_URL`:
```env
DATABASE_URL=sqlite:///./reflex_trainer.db
```

⚠️ **Lưu ý**: SQLite có giới hạn với UUID, nên dùng PostgreSQL cho production.

---

### 6️⃣ Cấu hình Secret Key

```bash
# Generate secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy output và paste vào .env
# SECRET_KEY=<your-generated-key>
```

**File .env hoàn chỉnh:**
```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/reflex_trainer

# JWT
SECRET_KEY=<your-generated-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# TTS
TTS_ENGINE=gtts
AUDIO_DIR=./audio

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Admin
FIRST_ADMIN_EMAIL=admin@example.com
FIRST_ADMIN_PASSWORD=changeme123

# Server
DEBUG=False
```

---

### 7️⃣ Chạy Migrations

```bash
# Kiểm tra Alembic config
alembic current

# Chạy migrations (tạo tables)
alembic upgrade head

# Verify
alembic current
# Should show: [current revision]
```

**Troubleshooting migrations**:
```bash
# Nếu lỗi
alembic stamp head
alembic revision --autogenerate -m "init"
alembic upgrade head
```

---

### 8️⃣ Seed Dữ liệu mẫu

```bash
python scripts/seed_data.py
```

**Sẽ tạo**:
- ✅ Admin user (admin@example.com / changeme123)
- ✅ 3 lessons (Greetings, Numbers, Common Phrases)
- ✅ 30 sentences (10 mỗi lesson)

**Verify**:
```bash
# PostgreSQL
psql reflex_trainer -c "SELECT COUNT(*) FROM lessons;"
psql reflex_trainer -c "SELECT COUNT(*) FROM sentences;"

# SQLite
sqlite3 reflex_trainer.db "SELECT COUNT(*) FROM lessons;"
```

---

### 9️⃣ Chạy Server

#### Development Mode (với hot reload):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
✅ Database tables created
INFO:     Application startup complete.
```

#### Production Mode (với Gunicorn):

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

### 🔟 Kiểm tra API

#### 1. Health Check:
```bash
curl http://localhost:8000/health
# Response: {"status":"ok","message":"API is running"}
```

#### 2. Interactive Docs:
Mở browser: **http://localhost:8000/docs**

#### 3. Test Register:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'
```

#### 4. Test Login:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "admin@example.com",
    "password": "changeme123"
  }'
```

#### 5. Get Lessons:
```bash
curl http://localhost:8000/api/v1/lessons
```

---

## 🎯 Các Lệnh Hữu Ích

### Server Management:

```bash
# Chạy dev server
./run.sh

# Chạy production server
./run.sh --prod

# Chạy trên port khác
./run.sh --port 3000

# Chạy với nhiều workers
./run.sh --prod --workers 8

# Stop server
Ctrl+C

# Kill process on port
kill -9 $(lsof -ti:8000)
```

### Database Management:

```bash
# Tạo migration mới
alembic revision --autogenerate -m "add new table"

# Apply migrations
alembic upgrade head

# Rollback 1 migration
alembic downgrade -1

# Reset database
alembic downgrade base
alembic upgrade head

# Re-seed data
python scripts/seed_data.py
```

### Virtual Environment:

```bash
# Kích hoạt venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Tắt venv
deactivate

# Xóa và tạo lại venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Testing:

```bash
# Chạy all tests
pytest

# Chạy với verbose
pytest -v

# Chạy specific test
pytest tests/test_api.py::test_health_check -v

# Chạy với coverage
pytest --cov=app tests/
```

### Dependencies:

```bash
# List installed packages
pip list

# Update requirements.txt
pip freeze > requirements.txt

# Install new package
pip install package-name
pip freeze > requirements.txt

# Update all packages
pip install --upgrade -r requirements.txt
```

---

## 🔍 Troubleshooting

### 1. Port đang được sử dụng

**Lỗi**: `Address already in use`

```bash
# Kiểm tra process
lsof -i :8000

# Kill process
kill -9 $(lsof -ti:8000)

# Hoặc chạy trên port khác
./run.sh --port 3000
```

### 2. Database connection error

**Lỗi**: `could not connect to server`

```bash
# Kiểm tra PostgreSQL
# macOS
brew services list | grep postgresql
brew services start postgresql

# Linux
sudo systemctl status postgresql
sudo systemctl start postgresql

# Test connection
psql -U postgres -h localhost -c "SELECT 1"
```

### 3. Import errors

**Lỗi**: `ModuleNotFoundError: No module named 'app'`

```bash
# Verify trong backend folder
pwd
# Should be: .../vi-en-reflex-trainer/backend

# Verify venv active
which python
# Should be: .../backend/venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### 4. Migration errors

**Lỗi**: `Can't locate revision identified by`

```bash
# Reset migrations
alembic stamp head
alembic upgrade head

# Hoặc recreate database
dropdb reflex_trainer  # PostgreSQL
createdb reflex_trainer
alembic upgrade head
python scripts/seed_data.py
```

### 5. Audio generation fails

**Lỗi**: `Failed to generate audio`

```bash
# Install espeak (cho pyttsx3)
# macOS
brew install espeak

# Linux
sudo apt-get install espeak

# Test gTTS
python3 -c "from gtts import gTTS; gTTS('test', lang='vi').save('test.mp3')"
```

### 6. Permission errors (macOS)

**Lỗi**: `Permission denied: './setup.sh'`

```bash
# Make scripts executable
chmod +x setup.sh run.sh

# Run
./setup.sh
```

---

## 📚 API Endpoints

Sau khi server chạy, truy cập:

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Quick Reference:

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | None | Health check |
| POST | `/api/v1/auth/register` | None | Đăng ký user |
| POST | `/api/v1/auth/login` | None | Đăng nhập |
| GET | `/api/v1/auth/me` | User | Thông tin user |
| GET | `/api/v1/lessons` | Guest | Danh sách lessons |
| GET | `/api/v1/sentences` | Guest | Danh sách sentences |
| GET | `/api/v1/audio/{id}/{lang}` | Guest | Audio file |
| GET | `/api/v1/practice/next` | Guest | Câu tiếp theo |
| POST | `/api/v1/practice/record` | Guest | Ghi nhận luyện tập |
| GET | `/api/v1/practice/stats` | User | Thống kê |

---

## 🎓 Next Steps

Sau khi API chạy thành công:

1. **Test với Postman/Insomnia**: Import OpenAPI schema
2. **Kết nối Frontend**: Update API base URL
3. **Setup CORS**: Thêm frontend URL vào `.env`
4. **Deploy Production**: Xem hướng dẫn trong README.md

---

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra [Troubleshooting](#-troubleshooting) section
2. Xem logs chi tiết: `tail -f logs/app.log`
3. Check requirements: `pip list`
4. Verify database: `psql reflex_trainer -c "\dt"`

---

**Happy coding! 🚀**
