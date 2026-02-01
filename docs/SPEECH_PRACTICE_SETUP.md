# Speech Practice Feature Setup Guide

## Overview

This guide explains how to set up and run the new Speech Practice feature alongside the existing VI-EN Reflex Trainer application.

## Architecture

The Speech Practice feature adds:
- **WebSocket API** for real-time audio streaming
- **Celery Workers** for parallel audio processing
- **Redis** for task queue and caching
- **MinIO** for audio storage (S3-compatible)
- **Multiple LLM providers** with automatic fallback

## Quick Start

### 1. Install Additional Dependencies

```bash
cd backend
pip install -r requirements-speech-practice.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp ../.env.speech-practice.example ../.env.speech-practice

# Edit and add your API keys
nano ../.env.speech-practice
```

Required environment variables:
- `OPENAI_API_KEY` - OpenAI API key
- `GEMINI_API_KEY` - Google Gemini API key  
- `DEEPSEEK_API_KEY` - DeepSeek API key
- `ENCRYPTION_KEY` - 32-byte key for encrypting API keys in DB

Generate encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Start Services

**Option A: Development (Existing + Speech Practice)**

```bash
# Start existing services (Postgres, Backend, Frontend)
docker-compose up -d

# Start speech practice services (Redis, MinIO, Celery workers)
docker-compose -f docker-compose.speech-practice.yml up -d
```

**Option B: All-in-One**

```bash
# Start everything
docker-compose -f docker-compose.yml -f docker-compose.speech-practice.yml up -d
```

### 4. Verify Services

Check all services are running:
```bash
docker-compose ps
```

You should see:
- ✅ `vi-en-postgres` (existing)
- ✅ `vi-en-backend` (existing)  
- ✅ `vi-en-frontend` (existing)
- ✅ `vi-en-redis` (new)
- ✅ `vi-en-minio` (new)
- ✅ `vi-en-worker-stt` (new)
- ✅ `vi-en-worker-prosody` (new)
- ✅ `vi-en-worker-llm` (new)
- ✅ `vi-en-celery-beat` (new)
- ✅ `vi-en-flower` (new - Celery monitor)

### 5. Access Services

- **API**: http://localhost:9999
- **API Docs**: http://localhost:9999/docs
- **Frontend**: http://localhost:80
- **MinIO Console**: http://localhost:9001 (admin/minioadmin)
- **Flower (Celery Monitor)**: http://localhost:5555

### 6. Initialize Database

Run migrations to create new tables:

```bash
# Enter backend container
docker exec -it vi-en-backend bash

# Run migrations
alembic upgrade head

# Seed LLM providers (optional)
python scripts/seed_llm_providers.py
```

### 7. Add LLM API Keys via Admin

1. Login as admin user
2. Go to `/admin/llm/providers`
3. Add API keys for each provider
4. Keys are automatically encrypted before storage

### 8. Test the Feature

Try the WebSocket endpoint:

```javascript
// In browser console or your frontend
const ws = new WebSocket('ws://localhost:9999/api/v1/ws/speech-practice?token=YOUR_JWT_TOKEN');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'start_session',
    mode: 'conversation'
  }));
};

ws.onmessage = (event) => {
  console.log('Server:', JSON.parse(event.data));
};
```

## Service Details

### Redis

- **Purpose**: Celery message broker, result backend, pub/sub for real-time updates
- **Port**: 6379
- **Data**: Persisted to `redis_data` volume

### MinIO

- **Purpose**: S3-compatible storage for audio files
- **Ports**: 
  - 9000 (API)
  - 9001 (Web Console)
- **Credentials**: minioadmin/minioadmin
- **Bucket**: `speech-practice-audio` (auto-created)

### Celery Workers

**STT Worker** (Speech-to-Text)
- Queue: `stt`
- Workers: 2
- Memory: 4GB
- CPU: 2 cores
- Purpose: Whisper transcription

**Prosody Worker**
- Queue: `prosody`
- Workers: 4
- Purpose: Audio feature extraction (librosa, parselmouth)

**LLM Worker**
- Queue: `llm`
- Workers: 4
- Purpose: LLM API orchestration with fallback

**Beat Scheduler**
- Purpose: Periodic tasks (cleanup, health checks)

### Flower

- Web UI for monitoring Celery tasks
- View task status, worker health, queue lengths
- Access at http://localhost:5555

## Development Workflow

### Running Locally (without Docker)

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: MinIO
minio server ~/minio-data --console-address ":9001"

# Terminal 3: FastAPI
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 4: Celery STT Worker
celery -A app.core.celery_app worker -Q stt -c 2 --loglevel=info

# Terminal 5: Celery Prosody Worker
celery -A app.core.celery_app worker -Q prosody -c 4 --loglevel=info

# Terminal 6: Celery LLM Worker
celery -A app.core.celery_app worker -Q llm -c 4 --loglevel=info

# Terminal 7: Celery Beat
celery -A app.core.celery_app beat --loglevel=info
```

### Monitoring Tasks

```bash
# View Celery tasks
celery -A app.core.celery_app inspect active

# Purge all tasks
celery -A app.core.celery_app purge

# Monitor Redis
redis-cli monitor
```

### Debug WebSocket

Use `wscat` for testing:

```bash
npm install -g wscat

wscat -c "ws://localhost:9999/api/v1/ws/speech-practice?token=YOUR_TOKEN"

# Send test message
> {"type":"start_session","mode":"conversation"}
```

## Troubleshooting

### Whisper Model Download Issues

If STT worker fails to download Whisper model:

```bash
# Pre-download model
docker exec -it vi-en-worker-stt bash
python -c "import whisper; whisper.load_model('turbo')"
```

### MinIO Bucket Not Created

```bash
# Create bucket manually
docker exec -it vi-en-minio bash
mc alias set myminio http://localhost:9000 minioadmin minioadmin
mc mb myminio/speech-practice-audio
```

### Celery Workers Not Processing

```bash
# Check worker status
docker logs vi-en-worker-stt
docker logs vi-en-worker-llm

# Restart workers
docker-compose -f docker-compose.speech-practice.yml restart celery_worker_stt
```

### LLM API Errors

```bash
# Check usage logs
docker exec -it vi-en-backend bash
python scripts/check_llm_usage.py

# Test provider health
curl http://localhost:9999/api/v1/admin/llm/providers
```

## Performance Tuning

### GPU Support for Whisper

Edit `docker-compose.speech-practice.yml`:

```yaml
celery_worker_stt:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  environment:
    WHISPER_DEVICE: cuda
```

### Scale Workers

```bash
# Increase STT workers
docker-compose -f docker-compose.speech-practice.yml up -d --scale celery_worker_stt=4

# Increase LLM workers
docker-compose -f docker-compose.speech-practice.yml up -d --scale celery_worker_llm=8
```

## Production Deployment

### Use Production Compose

```bash
docker-compose -f docker-compose.prod.yml -f docker-compose.speech-practice.yml up -d
```

### Environment Variables

Ensure these are set in production:

```bash
# Strong encryption key
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Production Redis (managed service recommended)
REDIS_URL=redis://:password@your-redis-host:6379/0

# Production S3 (or MinIO cluster)
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=YOUR_AWS_ACCESS_KEY
S3_SECRET_KEY=YOUR_AWS_SECRET_KEY

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
```

### Resource Recommendations

For 1000 concurrent users:
- **STT Workers**: 8-10 workers (GPU recommended)
- **Prosody Workers**: 10-15 workers
- **LLM Workers**: 15-20 workers
- **Redis**: Managed service with 4GB RAM
- **PostgreSQL**: 16GB RAM, SSD storage

## Monitoring & Alerts

### Prometheus Metrics

Metrics exposed at `http://localhost:9999/metrics`:
- `celery_task_duration_seconds`
- `llm_request_duration_seconds`
- `llm_token_usage_total`
- `websocket_connections_active`

### Sentry Error Tracking

Configure Sentry DSN in environment:
```bash
SENTRY_DSN=https://your-sentry-dsn
```

### Health Checks

- API: `GET /health`
- Celery: Flower UI at http://localhost:5555
- Redis: `redis-cli ping`
- MinIO: http://localhost:9000/minio/health/live

## Cost Optimization

### LLM Caching

Redis caches LLM responses for 1 hour. Expected cache hit rate: 60-80%.

### Token Rotation

Add multiple API keys per provider to distribute load and avoid rate limits.

### Cleanup Tasks

Automatic cleanup runs daily:
- Audio files older than 90 days deleted
- Temp files cleaned every hour

## Next Steps

1. ✅ Design document written: `docs/plans/2026-02-01-llm-speech-coach-design.md`
2. 📝 Ready to implement? See implementation plan in design doc
3. 🧪 Write tests following `tests/test_speech_practice.py` template
4. 🚀 Deploy to staging for user testing

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f [service-name]`
2. Review design doc: `docs/plans/2026-02-01-llm-speech-coach-design.md`
3. Monitor Flower: http://localhost:5555
4. Check Sentry for errors

---

**Happy Speech Practicing! 🎤🤖**
