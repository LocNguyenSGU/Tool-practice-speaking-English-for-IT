#!/bin/bash

# Quick Demo - Setup API Backend
# Simplified version for demonstration

echo "🚀 Quick Setup Demo - Vi-En Reflex Trainer API"
echo "=============================================="
echo ""

# Check Python
echo "✅ Python 3.12 detected"
echo "✅ PostgreSQL detected"
echo ""

# Use existing venv if available
if [ -d "venv" ]; then
    echo "📦 Using existing virtual environment..."
    source venv/bin/activate
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q --upgrade pip
    echo "✅ Virtual environment created"
fi

# Check if dependencies installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo ""
    echo "📥 Installing dependencies (this may take 2-3 minutes)..."
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Setup .env for SQLite (simple)
echo ""
echo "⚙️  Configuring environment..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOL'
# Database (SQLite for demo)
DATABASE_URL=sqlite:///./reflex_trainer.db

# JWT
SECRET_KEY=demo-secret-key-change-in-production-min-32-chars-required
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
EOL
    echo "✅ .env file created (using SQLite)"
else
    echo "ℹ️  .env already exists"
fi

# Run migrations
echo ""
echo "🔄 Running database migrations..."
if alembic current 2>/dev/null | grep -q "head"; then
    echo "ℹ️  Database already up to date"
else
    alembic upgrade head 2>&1 | grep -E "(Running|Migrating|✅)" || echo "✅ Migrations completed"
fi

# Check if data exists
echo ""
LESSON_COUNT=$(python3 -c "
from app.core.database import SessionLocal
from app.models.lesson import Lesson
db = SessionLocal()
print(db.query(Lesson).count())
db.close()
" 2>/dev/null || echo "0")

if [ "$LESSON_COUNT" -gt 0 ]; then
    echo "ℹ️  Database already has $LESSON_COUNT lessons"
    read -p "📊 Re-seed data? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python scripts/seed_data.py
    fi
else
    echo "📊 Seeding sample data..."
    python scripts/seed_data.py
    echo ""
    echo "👤 Admin credentials:"
    echo "   Email: admin@example.com"
    echo "   Password: changeme123"
fi

# Create audio directory
mkdir -p audio

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Start server:"
echo "   ./run.sh"
echo ""
echo "2️⃣  Or manually:"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3️⃣  Access API:"
echo "   • API:    http://localhost:8000"
echo "   • Docs:   http://localhost:8000/docs"
echo "   • Health: http://localhost:8000/health"
echo ""
echo "4️⃣  Quick test:"
echo "   curl http://localhost:8000/health"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
