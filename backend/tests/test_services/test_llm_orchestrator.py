import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session
from app.services.llm_orchestrator import LLMOrchestrator
from app.services.llm.base_client import LLMProviderError
from app.models.llm_provider import LLMProviderConfig, LLMAPIKey


@pytest.fixture
def db_with_providers(db: Session):
    """Create test providers and API keys"""
    # OpenAI provider
    openai = LLMProviderConfig(provider_name="openai", priority=1, is_active=True)
    db.add(openai)
    db.commit()
    db.refresh(openai)
    
    # Gemini provider
    gemini = LLMProviderConfig(provider_name="gemini", priority=2, is_active=True)
    db.add(gemini)
    db.commit()
    db.refresh(gemini)
    
    # Add API keys (encrypted dummy values)
    openai_key = LLMAPIKey(
        provider_id=openai.id,
        key_name="openai-key-1",
        api_key_encrypted="gAAAAABm...",  # Dummy encrypted value
        is_active=True
    )
    gemini_key = LLMAPIKey(
        provider_id=gemini.id,
        key_name="gemini-key-1",
        api_key_encrypted="gAAAAABm...",
        is_active=True
    )
    
    db.add_all([openai_key, gemini_key])
    db.commit()
    
    return db


@pytest.mark.asyncio
async def test_orchestrator_primary_provider_success(db_with_providers):
    """Test successful analysis using primary provider (OpenAI)"""
    orchestrator = LLMOrchestrator(db_with_providers, encryption_key="test-key-32-bytes!!!!!!!!!!!")
    
    # Mock OpenAI client success
    mock_result = {
        "scores": {"overall": 8.5, "pronunciation": 9.0},
        "feedback": {"conversational": "Tốt lắm!"},
        "provider": "openai"
    }
    
    # Mock key rotation service
    mock_key = MagicMock()
    mock_key.id = 1
    mock_key.api_key_encrypted = "encrypted"
    
    with patch.object(orchestrator.key_service, 'get_available_key', return_value=mock_key), \
         patch.object(orchestrator.key_service, 'decrypt_api_key', return_value="sk-test"), \
         patch.object(orchestrator.key_service, 'record_success'), \
         patch('app.services.llm_orchestrator.OpenAIClient') as MockOpenAI:
        
        mock_client = AsyncMock()
        mock_client.analyze_speech.return_value = mock_result
        mock_client.timeout = 10000
        MockOpenAI.return_value = mock_client
        
        result = await orchestrator.analyze_speech(
            transcript="Hello world",
            prosody_features={"pitch": {"mean": 180}},
            session_id="test-123",
            user_id=1
        )
        
        assert result["scores"]["overall"] == 8.5
        assert result["provider_used"] == "openai"
        assert result["was_degraded"] is False


@pytest.mark.asyncio
async def test_orchestrator_fallback_to_secondary(db_with_providers):
    """Test fallback to Gemini when OpenAI fails"""
    orchestrator = LLMOrchestrator(db_with_providers, encryption_key="test-key-32-bytes!!!!!!!!!!!")
    
    gemini_result = {
        "scores": {"overall": 9.0},
        "feedback": {"conversational": "Xuất sắc!"},
        "provider": "gemini"
    }
    
    # Mock key service
    mock_key = MagicMock()
    mock_key.id = 1
    
    call_count = [0]  # Track which provider is being called
    
    def get_key_side_effect(provider):
        call_count[0] += 1
        return mock_key
    
    with patch.object(orchestrator.key_service, 'get_available_key', side_effect=get_key_side_effect), \
         patch.object(orchestrator.key_service, 'decrypt_api_key', return_value="api-key"), \
         patch.object(orchestrator.key_service, 'record_failure'), \
         patch.object(orchestrator.key_service, 'record_success'), \
         patch('app.services.llm_orchestrator.OpenAIClient') as MockOpenAI, \
         patch('app.services.llm_orchestrator.GeminiClient') as MockGemini:
        
        # OpenAI fails
        mock_openai = AsyncMock()
        mock_openai.analyze_speech.side_effect = LLMProviderError("Rate limit", provider="openai")
        mock_openai.timeout = 10000
        MockOpenAI.return_value = mock_openai
        
        # Gemini succeeds
        mock_gemini = AsyncMock()
        mock_gemini.analyze_speech.return_value = gemini_result
        mock_gemini.timeout = 10000
        MockGemini.return_value = mock_gemini
        
        result = await orchestrator.analyze_speech(
            transcript="Good morning",
            prosody_features={"pitch": {"mean": 200}},
            session_id="test-456",
            user_id=2
        )
        
        assert result["scores"]["overall"] == 9.0
        assert result["provider_used"] == "gemini"
        assert result["was_degraded"] is False


@pytest.mark.asyncio
async def test_orchestrator_degraded_mode(db_with_providers):
    """Test degraded mode when all providers fail"""
    orchestrator = LLMOrchestrator(db_with_providers, encryption_key="test-key-32-bytes!!!!!!!!!!!")
    
    with patch('app.services.llm_orchestrator.OpenAIClient') as MockOpenAI, \
         patch('app.services.llm_orchestrator.GeminiClient') as MockGemini:
        
        # Both providers fail
        for MockClient in [MockOpenAI, MockGemini]:
            mock_client = AsyncMock()
            mock_client.analyze_speech.side_effect = Exception("API Error")
            mock_client.timeout = 10000
            MockClient.return_value = mock_client
        
        result = await orchestrator.analyze_speech(
            transcript="Test",
            prosody_features={},
            session_id="test-789",
            user_id=3
        )
        
        assert result["was_degraded"] is True
        assert "scores" in result
        assert result["provider_used"] == "degraded"


@pytest.mark.asyncio
async def test_orchestrator_timeout_triggers_fallback(db_with_providers):
    """Test that timeout on primary provider triggers fallback"""
    orchestrator = LLMOrchestrator(db_with_providers, encryption_key="test-key-32-bytes!!!!!!!!!!!")
    
    gemini_result = {"scores": {"overall": 8.0}, "provider": "gemini", "feedback": {"conversational": "OK"}}
    
    mock_key = MagicMock()
    mock_key.id = 1
    
    with patch.object(orchestrator.key_service, 'get_available_key', return_value=mock_key), \
         patch.object(orchestrator.key_service, 'decrypt_api_key', return_value="api-key"), \
         patch.object(orchestrator.key_service, 'record_failure'), \
         patch.object(orchestrator.key_service, 'record_success'), \
         patch('app.services.llm_orchestrator.OpenAIClient') as MockOpenAI, \
         patch('app.services.llm_orchestrator.GeminiClient') as MockGemini:
        
        # OpenAI times out
        mock_openai = AsyncMock()
        async def slow_analyze(*args, **kwargs):
            import asyncio
            await asyncio.sleep(20)  # Simulate slow response
        mock_openai.analyze_speech = slow_analyze
        mock_openai.timeout = 100  # Very short timeout
        MockOpenAI.return_value = mock_openai
        
        # Gemini succeeds
        mock_gemini = AsyncMock()
        mock_gemini.analyze_speech.return_value = gemini_result
        mock_gemini.timeout = 10000
        MockGemini.return_value = mock_gemini
        
        result = await orchestrator.analyze_speech(
            transcript="Timeout test",
            prosody_features={},
            session_id="test-timeout",
            user_id=4
        )
        
        assert result["provider_used"] == "gemini"


def test_create_client_openai(db_with_providers):
    """Test creating OpenAI client"""
    orchestrator = LLMOrchestrator(db_with_providers, encryption_key="test-key")
    
    with patch('app.services.llm_orchestrator.OpenAIClient') as MockOpenAI:
        orchestrator._create_client("openai", "sk-test-key")
        MockOpenAI.assert_called_once_with("sk-test-key")


def test_create_client_gemini(db_with_providers):
    """Test creating Gemini client"""
    orchestrator = LLMOrchestrator(db_with_providers, encryption_key="test-key")
    
    with patch('app.services.llm_orchestrator.GeminiClient') as MockGemini:
        orchestrator._create_client("gemini", "test-api-key")
        MockGemini.assert_called_once_with("test-api-key")
