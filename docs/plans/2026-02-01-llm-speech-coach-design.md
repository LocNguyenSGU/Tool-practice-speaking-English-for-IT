# LLM Speech Coach - System Design

**Date:** 2026-02-01  
**Feature:** AI-Powered Speech Practice with Prosody & Emotion Analysis  
**Status:** Design Complete - Ready for Implementation

---

## Executive Summary

This design introduces an AI speech coach feature that analyzes users' English pronunciation, prosody (rhythm, intonation, stress), and emotional tone. The system provides detailed, conversational feedback in Vietnamese to help learners improve their speaking skills.

### Key Capabilities

- **Real-time Audio Processing**: WebSocket streaming with progressive feedback (<4s total latency)
- **Multi-LLM Support**: OpenAI, Gemini, DeepSeek with automatic fallback and token rotation
- **Comprehensive Analysis**: Pronunciation, prosody, emotion, confidence, and fluency scoring
- **Two Practice Modes**: Free conversation and guided sentence practice
- **Analytics Dashboard**: Track progress, streaks, trends, and weak areas
- **Scalable Architecture**: Celery workers for parallel processing

---

## System Architecture

### High-Level Overview

```
┌─────────────┐
│   Browser   │ ← User records audio
└──────┬──────┘
       │ WebSocket (audio chunks)
       ↓
┌─────────────────────────────────────┐
│     FastAPI Application             │
│  ┌────────────────────────────┐    │
│  │ WebSocket Handler          │    │
│  │ - Receive audio chunks     │    │
│  │ - Send progress updates    │    │
│  └────────┬───────────────────┘    │
│           │ enqueue tasks           │
│  ┌────────▼───────────────────┐    │
│  │   Task Queue (Celery)      │    │
│  └────────────────────────────┘    │
└─────────────────────────────────────┘
           │
    ┌──────┴──────┬──────────┬────────────┐
    ↓             ↓          ↓            ↓
┌────────┐  ┌──────────┐ ┌─────────┐ ┌──────────┐
│STT     │  │Prosody   │ │LLM      │ │Analytics │
│Worker  │  │Extractor │ │Worker   │ │Worker    │
└────┬───┘  └────┬─────┘ └────┬────┘ └────┬─────┘
     │           │            │           │
     └───────────┴────────────┴───────────┘
                  │
            ┌─────▼──────┐
            │   Redis    │ ← Pub/Sub + Cache
            └────────────┘
                  │
    ┌─────────────┴─────────────┐
    ↓                           ↓
┌──────────┐              ┌──────────┐
│PostgreSQL│              │  S3/MinIO│
│Analytics │              │  Audio   │
└──────────┘              └──────────┘
```

### Technology Stack

- **API Framework**: FastAPI (existing)
- **Task Queue**: Celery + Redis
- **Speech-to-Text**: OpenAI Whisper (self-hosted)
- **Audio Analysis**: librosa + parselmouth (Praat)
- **LLM Providers**: OpenAI GPT-4o, Gemini 2.0, DeepSeek
- **Storage**: PostgreSQL + S3/MinIO
- **Real-time**: WebSocket + Redis Pub/Sub

---

## Core Components

### 1. WebSocket Communication Layer

**Protocol Design:**

Client → Server Messages:
- `start_session`: Initialize practice session
- `audio_chunk`: Stream audio data (~100ms chunks)
- `end_recording`: Finalize recording
- `retry`: Retry failed analysis

Server → Client Messages:
- `session_started`: Confirm session creation
- `progress`: Incremental updates (0-100%)
- `transcription`: Speech-to-text result
- `prosody_features`: Extracted audio features
- `analysis_complete`: Final scores and feedback
- `error`: Error with retry information

**Progressive Feedback Timeline:**
```
0-1s:   Listening... (live waveform)
1-2s:   Transcribing... (partial transcript)
2-3s:   Analyzing prosody...
3-4s:   AI feedback ready!
```

### 2. Audio Processing Pipeline

**Step 1: Speech-to-Text (Whisper)**
- Model: `large-v3-turbo` (balance of speed/accuracy)
- Word-level timestamps for prosody alignment
- Confidence scoring from log probabilities
- Fallback to `base` model on resource constraints

**Step 2: Prosody Feature Extraction**

Features extracted:
```python
{
  "pitch": {
    "mean": 180.5,      # Hz
    "std": 25.3,        # Variation
    "range": 120.0,     # Dynamic range
    "contour": [...]    # Full pitch curve
  },
  "energy": {
    "mean": 0.65,       # Loudness
    "dynamic_range": 0.4
  },
  "speaking_rate": {
    "syllables_per_second": 4.2,
    "words_per_minute": 140
  },
  "pauses": {
    "count": 3,
    "avg_duration": 0.5,  # seconds
    "positions": [...]
  },
  "confidence": {
    "pitch_stability": 0.85,      # 0-1
    "energy_consistency": 0.78,
    "hesitation_score": 0.3       # Lower = better
  }
}
```

**Libraries Used:**
- `librosa`: General audio analysis (pitch, energy, tempo)
- `parselmouth` (Praat): Specialized speech metrics (jitter, shimmer)

### 3. Multi-LLM Orchestration

**Provider Strategy:**

```python
PROVIDER_CHAIN = [
    "openai",    # Primary (best prosody analysis)
    "gemini",    # Secondary (multimodal strengths)
    "deepseek"   # Tertiary (cost-effective fallback)
]
```

**Features:**

1. **Token Rotation**:
   - Multiple API keys per provider
   - Round-robin + least-recently-used strategy
   - Automatic rate limit detection and reset

2. **Circuit Breaker**:
   - Track consecutive failures
   - Open circuit after 5 failures
   - Auto-recovery after timeout

3. **Fallback Chain**:
   - Try primary → secondary → tertiary
   - Graceful degradation if all fail
   - Rule-based scoring as last resort

4. **Response Caching**:
   - Redis cache with 1-hour TTL
   - Cache key: hash(transcript + prosody features)
   - Reduces cost and improves latency

### 4. LLM Analysis Prompt

**Input to LLM:**
```
Transcript: "Hello, how are you doing today?"
Reference (if sentence mode): "Hello, how are you?"

Prosody Data:
- Pitch: 180Hz (±25Hz variation)
- Speaking rate: 4.2 syllables/sec
- Pauses: 3 pauses, avg 0.5s
- Confidence indicators: moderate

Task: Analyze and provide scores + Vietnamese feedback
```

**Output Format:**
```json
{
  "scores": {
    "overall": 8.5,
    "pronunciation": 9.0,
    "prosody": 7.5,
    "emotion": 8.0,
    "confidence": 7.0,
    "fluency": 9.0
  },
  "feedback": {
    "conversational": "Good job! Phát âm rất rõ ràng (9/10). Tuy nhiên tôi nhận thấy ngữ điệu hơi thiếu tự tin - giọng bạn đi xuống ở chỗ nên đi lên. Có 3 khoảng lặng hơi dài, cho thấy bạn đang suy nghĩ. Thử lại với nhiều năng lượng hơn nhé!",
    "detailed": {
      "strengths": [
        "Phát âm từng từ rất rõ ràng",
        "Tốc độ nói vừa phải, dễ nghe"
      ],
      "improvements": [
        "Nhấn mạnh vào 'really' nếu muốn thể hiện sự quan tâm",
        "Tăng intonation ở cuối câu hỏi (giọng lên)",
        "Giảm khoảng lặng giữa các từ"
      ],
      "emotion_detected": "neutral_polite",
      "confidence_level": "moderate",
      "prosody_notes": "Giọng hơi đơn điệu, thiếu biến thiên cao độ ở phần nhấn mạnh. Ngữ điệu này phù hợp với một cuộc trò chuyện thông thường, nhưng nếu muốn thể hiện nhiệt tình hơn thì cần thêm năng lượng."
    }
  }
}
```

---

## Database Schema

### New Tables

**1. LLM Provider Configuration**
```sql
CREATE TABLE llm_providers (
    id SERIAL PRIMARY KEY,
    provider_name VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    requests_per_minute INTEGER DEFAULT 60,
    failure_threshold INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 60,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**2. LLM API Keys (Token Rotation)**
```sql
CREATE TABLE llm_api_keys (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES llm_providers(id),
    key_name VARCHAR(100),
    api_key_encrypted TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_rate_limited BOOLEAN DEFAULT FALSE,
    rate_limit_reset_at TIMESTAMP,
    total_requests INTEGER DEFAULT 0,
    total_tokens_used BIGINT DEFAULT 0,
    total_cost_usd FLOAT DEFAULT 0.0,
    last_used_at TIMESTAMP,
    last_success_at TIMESTAMP,
    last_failure_at TIMESTAMP,
    consecutive_failures INTEGER DEFAULT 0,
    daily_request_limit INTEGER,
    monthly_budget_usd FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**3. LLM Usage Logs**
```sql
CREATE TABLE llm_usage_logs (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES llm_providers(id),
    api_key_id INTEGER REFERENCES llm_api_keys(id),
    session_id VARCHAR(36) REFERENCES speech_practice_sessions(id),
    user_id INTEGER REFERENCES users(id),
    model_used VARCHAR(100),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    response_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    estimated_cost_usd FLOAT,
    was_fallback BOOLEAN DEFAULT FALSE,
    attempt_number INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**4. Speech Practice Sessions**
```sql
CREATE TABLE speech_practice_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    mode VARCHAR(20) NOT NULL,  -- 'conversation' or 'sentence_practice'
    sentence_id INTEGER REFERENCES sentences(id),
    audio_url VARCHAR(500),
    audio_duration_seconds FLOAT,
    audio_size_bytes INTEGER,
    transcript TEXT,
    reference_text TEXT,
    transcription_confidence FLOAT,
    prosody_features JSONB,
    analysis_result JSONB,
    overall_score FLOAT,
    pronunciation_score FLOAT,
    prosody_score FLOAT,
    emotion_score FLOAT,
    confidence_score FLOAT,
    fluency_score FLOAT,
    conversational_feedback TEXT,
    detailed_feedback JSONB,
    llm_provider_used VARCHAR(50),
    processing_time_ms INTEGER,
    was_degraded_mode BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'processing',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

**5. User Progress (Speech Practice)**
```sql
CREATE TABLE user_progress_llm (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    total_sessions INTEGER DEFAULT 0,
    total_practice_time_seconds INTEGER DEFAULT 0,
    avg_overall_score FLOAT,
    avg_pronunciation_score FLOAT,
    avg_prosody_score FLOAT,
    avg_confidence_score FLOAT,
    score_trend FLOAT,  -- Positive = improving
    current_streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,
    last_practice_date DATE,
    weak_areas JSONB,  -- ["prosody", "confidence"]
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints

### Speech Practice APIs

```
POST   /api/v1/speech-practice/sessions
GET    /api/v1/speech-practice/sessions/{id}
GET    /api/v1/speech-practice/sessions
GET    /api/v1/speech-practice/progress
GET    /api/v1/speech-practice/analytics/trends
```

### Admin LLM Management

```
GET    /api/v1/admin/llm/providers
POST   /api/v1/admin/llm/providers/{name}/keys
PATCH  /api/v1/admin/llm/keys/{id}
GET    /api/v1/admin/llm/usage/stats
```

### WebSocket

```
WS     /api/v1/ws/speech-practice
```

---

## Deployment Architecture

### Services

1. **FastAPI App**: Main API + WebSocket handler
2. **Celery Worker - STT**: Whisper transcription (CPU/GPU intensive)
3. **Celery Worker - Prosody**: Audio feature extraction
4. **Celery Worker - LLM**: LLM API orchestration
5. **Celery Beat**: Scheduled tasks (cleanup, health checks)
6. **Redis**: Message broker + Pub/Sub + Cache
7. **PostgreSQL**: Data persistence
8. **MinIO/S3**: Audio file storage
9. **Flower**: Celery monitoring

### Resource Requirements

- **STT Worker**: 2-4 CPUs, 4GB RAM (or 1 GPU)
- **Prosody Worker**: 1-2 CPUs, 2GB RAM
- **LLM Worker**: 1-2 CPUs, 1GB RAM (network-bound)
- **Redis**: 2GB RAM
- **PostgreSQL**: 4GB RAM

### Scaling Strategy

- **Horizontal**: Add more Celery workers per queue
- **Vertical**: Upgrade STT workers with GPU
- **Caching**: Redis for LLM responses (60-80% hit rate expected)

---

## Performance Optimization

### Latency Breakdown (Target)

```
Audio Upload (streaming):     0ms (parallel)
STT (Whisper turbo):          1-2s
Prosody Extraction:           0.5-1s
LLM Analysis:                 2-3s
─────────────────────────────────
Total (worst case):           ~4s
Perceived latency:            <1s (progressive updates)
```

### Optimization Techniques

1. **Model Pre-loading**: Whisper warm in worker memory
2. **Parallel Processing**: STT + Prosody run concurrently
3. **Early Streaming**: Send transcript before analysis complete
4. **Response Caching**: Cache LLM responses for common patterns
5. **Token Rotation**: Distribute load across multiple API keys
6. **Circuit Breakers**: Avoid cascading failures

---

## Error Handling Strategy

### Failure Scenarios

1. **STT Fails**: Return partial/no transcript → basic scoring only
2. **Prosody Fails**: Use minimal features → reduced analysis quality
3. **All LLMs Fail**: Rule-based scoring + generic feedback
4. **Audio Upload Fails**: Save session without audio, allow retry
5. **Network Issues**: WebSocket reconnection with session resume

### Degraded Mode

When all LLMs unavailable:
```json
{
  "scores": {
    "overall": 7.0,
    "confidence": 5.0  // from prosody features
  },
  "feedback": {
    "conversational": "Hệ thống AI đang bận, đây là phân tích sơ bộ: Bạn nói với độ tự tin 5.0/10."
  },
  "degraded_mode": true
}
```

---

## Security Considerations

1. **API Key Encryption**: Fernet encryption for LLM keys in DB
2. **WebSocket Auth**: JWT token validation on connection
3. **Rate Limiting**: Per-user session limits (20/hour)
4. **Audio Validation**: Max size (10MB), duration (60s), format check
5. **CORS**: Restrict origins for WebSocket connections

---

## Testing Strategy

### Unit Tests
- Audio processing functions
- Prosody feature extraction
- LLM provider clients
- Token rotation logic

### Integration Tests
- WebSocket session flow
- Celery task execution
- Database operations
- LLM fallback chain

### Performance Tests
- STT processing time (<2s for 5s audio)
- LLM response time (<5s)
- WebSocket concurrent connections (1000+)
- End-to-end latency (<4s)

### Load Tests
- 100 concurrent users
- 1000 sessions/hour
- Token rotation under load
- Circuit breaker activation

---

## Monitoring & Alerts

### Metrics to Track

- Request rate per LLM provider
- LLM response times (p50, p95, p99)
- Token usage and costs
- Fallback occurrence rate
- WebSocket connection count
- Celery queue lengths
- STT processing times
- Error rates by type

### Alerts

- **Critical**: All LLM providers down
- **High**: Primary LLM consistently failing (>50%)
- **Medium**: Celery queue backlog >100 tasks
- **Low**: Daily cost exceeds budget

---

## Future Enhancements

1. **Real-time Pronunciation Correction**: Stream corrections during speaking
2. **Voice Cloning**: Generate native speaker examples with user's content
3. **Conversation Partner**: AI responds and continues dialogue
4. **Accent Detection**: Identify and help reduce specific accent patterns
5. **Mobile SDK**: Native iOS/Android for better audio quality
6. **Gamification**: Achievements, leaderboards, challenges

---

## Migration from Current System

### Phase 1: Infrastructure Setup
- Add Redis, Celery, MinIO to docker-compose
- Database migrations for new tables
- Install audio processing libraries

### Phase 2: Core Implementation
- WebSocket endpoint
- Audio processing pipeline
- LLM orchestration layer

### Phase 3: Integration
- Frontend WebSocket client
- Admin dashboard for LLM management
- Analytics dashboard

### Phase 4: Testing & Optimization
- Load testing
- Performance tuning
- User acceptance testing

---

## Cost Estimation

### Monthly Costs (1000 active users, 20 sessions each)

**LLM API Costs:**
- OpenAI GPT-4o: 20,000 sessions × $0.02 = $400
- Fallback usage: ~10% × $0.01 = $20
- **Total LLM**: ~$420/month

**Infrastructure:**
- Redis: $10/month (managed)
- MinIO: $20/month (storage)
- Additional compute: $50/month
- **Total Infra**: ~$80/month

**Grand Total**: ~$500/month for 20k sessions
**Per Session**: $0.025

---

## Success Metrics

### Technical
- [ ] Average latency < 4s
- [ ] LLM fallback rate < 5%
- [ ] WebSocket uptime > 99.5%
- [ ] Cache hit rate > 60%

### Product
- [ ] User engagement: 5+ sessions/week
- [ ] Score improvement: +10% over 30 days
- [ ] User satisfaction: 4.5+ stars
- [ ] Retention: 70% after 1 month

---

## Conclusion

This design provides a production-ready, scalable architecture for AI-powered speech coaching. The system balances:

- **Performance**: <4s latency through progressive feedback
- **Reliability**: Multi-provider fallback with 99.5%+ uptime
- **Cost**: ~$0.025/session through caching and optimization
- **Quality**: Comprehensive prosody and emotion analysis
- **Scalability**: Horizontal scaling via Celery workers

Ready for implementation with clear separation of concerns and comprehensive error handling.
