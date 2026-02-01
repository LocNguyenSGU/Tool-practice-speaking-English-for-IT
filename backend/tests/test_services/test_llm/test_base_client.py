import pytest
from app.services.llm.base_client import BaseLLMClient, LLMProviderError

class MockLLMClient(BaseLLMClient):
    """Mock implementation for testing"""
    async def analyze_speech(self, transcript, prosody_features, reference_text=None, mode="conversation"):
        return {
            "scores": {"overall": 8.5},
            "feedback": {"conversational": "Good job!"}
        }
    
    async def health_check(self):
        return True

def test_base_client_initialization():
    client = MockLLMClient(api_key="test-key", timeout=5000)
    assert client.api_key == "test-key"
    assert client.timeout == 5000

@pytest.mark.asyncio
async def test_mock_analyze_speech():
    client = MockLLMClient(api_key="test-key")
    result = await client.analyze_speech("Hello world", {"pitch": {"mean": 180}})
    assert result["scores"]["overall"] == 8.5

@pytest.mark.asyncio
async def test_health_check():
    client = MockLLMClient(api_key="test-key")
    assert await client.health_check() == True

def test_llm_provider_error():
    error = LLMProviderError("Test error", provider="openai")
    assert str(error) == "Test error"
    assert error.provider == "openai"
