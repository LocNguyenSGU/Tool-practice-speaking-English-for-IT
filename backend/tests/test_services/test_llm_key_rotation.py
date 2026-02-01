import pytest
from app.services.llm_key_rotation import LLMKeyRotationService
from app.models.llm_provider import LLMProviderConfig, LLMAPIKey
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

def test_get_available_key(db: Session):
    # Create provider
    provider = LLMProviderConfig(
        provider_name="openai",
        is_active=True,
        priority=1
    )
    db.add(provider)
    db.commit()
    
    # Create API key
    service = LLMKeyRotationService(db, "test-encryption-key-32bytes!!")
    encrypted = service.encrypt_api_key("sk-test-123")
    
    api_key = LLMAPIKey(
        provider_id=provider.id,
        key_name="test-key-1",
        api_key_encrypted=encrypted,
        is_active=True
    )
    db.add(api_key)
    db.commit()
    
    # Get available key
    key = service.get_available_key("openai")
    assert key is not None
    assert key.provider.provider_name == "openai"

def test_get_available_key_rotation(db: Session):
    # Create provider with multiple keys
    provider = LLMProviderConfig(provider_name="gemini", is_active=True)
    db.add(provider)
    db.commit()
    
    service = LLMKeyRotationService(db, "test-encryption-key-32bytes!!")
    
    # Create 3 API keys
    for i in range(3):
        encrypted = service.encrypt_api_key(f"sk-test-{i}")
        key = LLMAPIKey(
            provider_id=provider.id,
            key_name=f"key-{i}",
            api_key_encrypted=encrypted,
            is_active=True
        )
        db.add(key)
    db.commit()
    
    # Get keys multiple times - should rotate (least recently used)
    key1 = service.get_available_key("gemini")
    key1.last_used_at = datetime.utcnow()
    db.commit()
    
    key2 = service.get_available_key("gemini")
    key2.last_used_at = datetime.utcnow()
    db.commit()
    
    key3 = service.get_available_key("gemini")
    
    # Should get different keys (rotation)
    assert key1.id != key2.id

def test_record_success_updates_stats(db: Session):
    provider = LLMProviderConfig(provider_name="openai", is_active=True)
    db.add(provider)
    db.commit()
    
    service = LLMKeyRotationService(db, "test-encryption-key-32bytes!!")
    encrypted = service.encrypt_api_key("sk-test-456")
    
    key = LLMAPIKey(
        provider_id=provider.id,
        key_name="success-key",
        api_key_encrypted=encrypted,
        is_active=True
    )
    db.add(key)
    db.commit()
    
    # Record success
    service.record_success(key.id, tokens_used=100, latency_seconds=0.5)
    
    db.refresh(key)
    assert key.request_count == 1
    assert key.failure_count == 0

def test_record_failure_increments_count(db: Session):
    provider = LLMProviderConfig(provider_name="openai", is_active=True)
    db.add(provider)
    db.commit()
    
    service = LLMKeyRotationService(db, "test-encryption-key-32bytes!!")
    encrypted = service.encrypt_api_key("sk-test-789")
    
    key = LLMAPIKey(
        provider_id=provider.id,
        key_name="fail-key",
        api_key_encrypted=encrypted,
        is_active=True
    )
    db.add(key)
    db.commit()
    
    # Record failure
    service.record_failure(key.id, "Rate limit exceeded")
    
    db.refresh(key)
    assert key.failure_count == 1
    assert key.last_failure_at is not None

def test_decrypt_api_key(db: Session):
    service = LLMKeyRotationService(db, "test-encryption-key-32bytes!!")
    
    original = "sk-test-secret-key"
    encrypted = service.encrypt_api_key(original)
    decrypted = service.decrypt_api_key(encrypted)
    
    assert decrypted == original
    assert encrypted != original
