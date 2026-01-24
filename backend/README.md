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
