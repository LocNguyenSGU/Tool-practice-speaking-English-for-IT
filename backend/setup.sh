#!/bin/bash

# Vi-En Reflex Trainer API - Setup Script
# Tự động cài đặt môi trường và database

set -e  # Exit on error

echo "🚀 Vi-En Reflex Trainer API - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "📌 Kiểm tra Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 chưa được cài đặt!"
    echo "   Cài đặt: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION detected"

# Check PostgreSQL
echo ""
echo "📌 Kiểm tra PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL chưa được cài đặt!"
    echo "   macOS: brew install postgresql"
    echo "   Ubuntu: sudo apt-get install postgresql"
    echo ""
    read -p "Tiếp tục với SQLite cho testing? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    USE_SQLITE=true
else
    echo "✅ PostgreSQL detected"
    USE_SQLITE=false
fi

# Create virtual environment
echo ""
echo "📦 Tạo virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  venv đã tồn tại, xóa và tạo mới..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "🔌 Kích hoạt virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "⬆️  Nâng cấp pip..."
pip install --upgrade pip -q
echo "✅ pip upgraded"

# Install dependencies
echo ""
echo "📥 Cài đặt dependencies..."
echo "   (Quá trình này có thể mất vài phút...)"
pip install -r requirements.txt -q
echo "✅ Dependencies installed"

# Create .env file if not exists
echo ""
echo "⚙️  Cấu hình environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env file created"
    
    # Generate secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    if [ "$USE_SQLITE" = true ]; then
        # Configure for SQLite
        echo "   Cấu hình SQLite cho testing..."
        sed -i.bak "s|DATABASE_URL=.*|DATABASE_URL=sqlite:///./reflex_trainer.db|g" .env
        sed -i.bak "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" .env
    else
        # Configure for PostgreSQL
        echo ""
        echo "📝 Nhập thông tin PostgreSQL:"
        read -p "   Database host (localhost): " DB_HOST
        DB_HOST=${DB_HOST:-localhost}
        
        read -p "   Database port (5434): " DB_PORT
        DB_PORT=${DB_PORT:-5434}
        
        read -p "   Database name (vi_en_trainer): " DB_NAME
        DB_NAME=${DB_NAME:-vi_en_trainer}
        
        read -p "   Database user (postgres): " DB_USER
        DB_USER=${DB_USER:-postgres}
        
        read -sp "   Database password (mysecretpassword): " DB_PASSWORD
        DB_PASSWORD=${DB_PASSWORD:-mysecretpassword}
        echo ""
        
        # Update .env
        DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
        sed -i.bak "s|DATABASE_URL=.*|DATABASE_URL=$DATABASE_URL|g" .env
        sed -i.bak "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" .env
        
        # Create database if not exists
        echo ""
        echo "🗄️  Tạo database..."
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
        PGPASSWORD=$DB_PASSWORD createdb -h $DB_HOST -U $DB_USER $DB_NAME
        echo "✅ Database created/verified"
    fi
    
    rm -f .env.bak
    echo "✅ Environment configured"
else
    echo "ℹ️  .env đã tồn tại, giữ nguyên cấu hình"
fi

# Run migrations
echo ""
echo "🔄 Chạy database migrations..."
alembic upgrade head
echo "✅ Migrations completed"

# Seed data
echo ""
read -p "📊 Seed dữ liệu mẫu? (3 lessons + admin user) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python scripts/seed_data.py
    echo "✅ Sample data seeded"
    echo ""
    echo "👤 Admin credentials:"
    echo "   Email: admin@example.com"
    echo "   Password: changeme123"
fi

# Create audio directory
echo ""
echo "📁 Tạo audio directory..."
mkdir -p audio
echo "✅ Audio directory created"

# Success message
echo ""
echo "🎉 Setup hoàn tất!"
echo ""
echo "📖 Các lệnh hữu ích:"
echo "   ./run.sh               - Chạy API server"
echo "   ./run.sh --prod        - Chạy production mode"
echo "   source venv/bin/activate - Kích hoạt venv"
echo "   deactivate             - Tắt venv"
echo ""
echo "📚 API Documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "💡 Để chạy server ngay:"
echo "   ./run.sh"
echo ""
