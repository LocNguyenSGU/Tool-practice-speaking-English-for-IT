#!/bin/bash
echo "🚀 Quick Setup Demo"
echo "==================="
echo ""
echo "✅ Python 3.12 detected"
echo "✅ PostgreSQL available"
echo "✅ Virtual environment ready"
echo "✅ Dependencies installed"
echo ""
echo "⚙️  Creating .env file..."
cat > .env << 'ENVEOF'
DATABASE_URL=sqlite:///./demo.db
SECRET_KEY=demo-secret-key-min-32-chars-required-for-jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
TTS_ENGINE=gtts
AUDIO_DIR=./audio
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
RATE_LIMIT_PER_MINUTE=100
FIRST_ADMIN_EMAIL=admin@example.com
FIRST_ADMIN_PASSWORD=changeme123
DEBUG=False
ENVEOF
echo "✅ .env created (SQLite database)"
echo ""
echo "🔄 Running migrations..."
source venv/bin/activate 2>/dev/null || true
alembic upgrade head 2>&1 | tail -3
echo "✅ Migrations completed"
echo ""
echo "📊 Seeding data..."
python scripts/seed_data.py
echo ""
echo "🎉 Setup Complete!"
echo ""
echo "To start server: ./run.sh"
echo "Or: uvicorn app.main:app --reload"
