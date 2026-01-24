#!/bin/bash

# Vi-En Reflex Trainer API - Run Script
# Chạy API server với các options khác nhau

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Vi-En Reflex Trainer API${NC}"
echo "================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment chưa được tạo!${NC}"
    echo "   Chạy: ./setup.sh"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ File .env chưa tồn tại!${NC}"
    echo "   Chạy: ./setup.sh"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}🔌 Kích hoạt virtual environment...${NC}"
source venv/bin/activate

# Parse arguments
MODE="dev"
HOST="0.0.0.0"
PORT="8000"
WORKERS="1"

while [[ $# -gt 0 ]]; do
    case $1 in
        --prod|--production)
            MODE="prod"
            WORKERS="4"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./run.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --prod, --production    Chạy production mode (4 workers)"
            echo "  --port PORT             Đổi port (default: 8000)"
            echo "  --host HOST             Đổi host (default: 0.0.0.0)"
            echo "  --workers NUM           Số workers cho production (default: 4)"
            echo "  --help, -h              Hiển thị help"
            echo ""
            echo "Examples:"
            echo "  ./run.sh                        # Dev mode với reload"
            echo "  ./run.sh --prod                 # Production mode"
            echo "  ./run.sh --port 3000            # Chạy trên port 3000"
            echo "  ./run.sh --prod --workers 8     # Production với 8 workers"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage"
            exit 1
            ;;
    esac
done

# Check if port is available
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port $PORT đang được sử dụng!${NC}"
    echo -e "   Processes sử dụng port $PORT:"
    lsof -Pi :$PORT -sTCP:LISTEN
    echo ""
    echo "   Kill process: kill -9 \$(lsof -ti:$PORT)"
    exit 1
fi

# Display config
echo ""
echo -e "${YELLOW}⚙️  Configuration:${NC}"
echo "   Mode: $MODE"
echo "   Host: $HOST"
echo "   Port: $PORT"
if [ "$MODE" = "prod" ]; then
    echo "   Workers: $WORKERS"
fi
echo ""

# Run server based on mode
if [ "$MODE" = "dev" ]; then
    echo -e "${GREEN}🔥 Starting development server với hot reload...${NC}"
    echo ""
    echo -e "${BLUE}📚 API Documentation:${NC}"
    echo "   Swagger UI: http://localhost:$PORT/docs"
    echo "   ReDoc:      http://localhost:$PORT/redoc"
    echo "   Health:     http://localhost:$PORT/health"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo ""
    
    uvicorn app.main:app --reload --host $HOST --port $PORT
    
else
    echo -e "${GREEN}🚀 Starting production server...${NC}"
    echo ""
    
    # Check if gunicorn is installed
    if ! command -v gunicorn &> /dev/null; then
        echo -e "${YELLOW}⚠️  gunicorn chưa được cài đặt, installing...${NC}"
        pip install gunicorn
    fi
    
    echo -e "${BLUE}📚 API Documentation:${NC}"
    echo "   Swagger UI: http://localhost:$PORT/docs"
    echo "   ReDoc:      http://localhost:$PORT/redoc"
    echo "   Health:     http://localhost:$PORT/health"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo ""
    
    gunicorn app.main:app \
        --workers $WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind $HOST:$PORT \
        --access-logfile - \
        --error-logfile - \
        --log-level info
fi
