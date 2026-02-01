import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.llm.gemini_client import GeminiClient
from app.services.llm.base_client import LLMProviderError


@pytest.mark.asyncio
async def test_gemini_client_initialization():
    client = GeminiClient(api_key="test-key", model="gemini-2.0-flash-exp", timeout=8000)
    assert client.api_key == "test-key"
    assert client.model_name == "gemini-2.0-flash-exp"
    assert client.timeout == 8000
    assert client.name == "gemini"


@pytest.mark.asyncio
async def test_analyze_speech_success():
    client = GeminiClient(api_key="test-key")
    
    # Mock Gemini response
    mock_response = MagicMock()
    mock_response.text = '{"scores": {"overall": 9.0, "fluency": 8.5}, "feedback": {"conversational": "Xuất sắc!"}}'
    
    with patch.object(client.model, 'generate_content_async', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        result = await client.analyze_speech(
            transcript="How are you today?",
            prosody_features={"pitch": {"mean": 200}, "speaking_rate": {"syllables_per_second": 4.0}}
        )
        
        assert result["scores"]["overall"] == 9.0
        assert result["scores"]["fluency"] == 8.5
        assert "conversational" in result["feedback"]
        assert result["provider"] == "gemini"
        assert result["model"] == "gemini-2.0-flash-exp"


@pytest.mark.asyncio
async def test_analyze_speech_with_reference():
    client = GeminiClient(api_key="test-key")
    
    mock_response = MagicMock()
    mock_response.text = '{"scores": {"overall": 8.0}, "feedback": {"conversational": "Khá tốt"}}'
    
    with patch.object(client.model, 'generate_content_async', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        result = await client.analyze_speech(
            transcript="Good morning",
            prosody_features={"pitch": {"mean": 180}},
            reference_text="Good morning everyone",
            mode="sentence_practice"
        )
        
        assert result["scores"]["overall"] == 8.0
        mock_generate.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_speech_api_error():
    client = GeminiClient(api_key="test-key")
    
    with patch.object(client.model, 'generate_content_async', new_callable=AsyncMock) as mock_generate:
        mock_generate.side_effect = Exception("API quota exceeded")
        
        with pytest.raises(LLMProviderError) as exc_info:
            await client.analyze_speech("Test", {"pitch": {"mean": 150}})
        
        assert "Gemini failed" in str(exc_info.value)
        assert exc_info.value.provider == "gemini"


@pytest.mark.asyncio
async def test_health_check_success():
    client = GeminiClient(api_key="test-key")
    
    mock_response = MagicMock()
    mock_response.text = "OK"
    
    with patch.object(client.model, 'generate_content_async', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        result = await client.health_check()
        assert result is True


@pytest.mark.asyncio
async def test_health_check_failure():
    client = GeminiClient(api_key="test-key")
    
    with patch.object(client.model, 'generate_content_async', new_callable=AsyncMock) as mock_generate:
        mock_generate.side_effect = Exception("Network error")
        
        result = await client.health_check()
        assert result is False
