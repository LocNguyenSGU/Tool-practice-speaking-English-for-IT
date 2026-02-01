import pytest
from app.models.llm_provider import LLMProviderConfig, LLMAPIKey
from sqlalchemy.orm import Session

def test_create_llm_provider(db: Session):
    provider = LLMProviderConfig(
        provider_name="openai",
        is_active=True,
        priority=1,
        requests_per_minute=60
    )
    db.add(provider)
    db.commit()
    
    assert provider.id is not None
    assert provider.provider_name == "openai"

def test_add_api_key_to_provider(db: Session):
    provider = LLMProviderConfig(provider_name="gemini")  # Use different provider
    db.add(provider)
    db.commit()
    
    api_key = LLMAPIKey(
        provider_id=provider.id,
        key_name="production-key-1",
        api_key_encrypted="encrypted-key-here",
        is_active=True
    )
    db.add(api_key)
    db.commit()
    
    assert api_key.id is not None
    assert len(provider.api_keys) == 1
