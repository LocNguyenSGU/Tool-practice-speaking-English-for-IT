import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.llm.openai_client import OpenAIClient
from app.services.llm.base_client import LLMProviderError


@pytest.mark.asyncio
async def test_openai_client_initialization():
    client = OpenAIClient(api_key="test-key", model="gpt-4o", timeout=5000)
    assert client.api_key == "test-key"
    assert client.model == "gpt-4o"
    assert client.timeout == 5000
    assert client.name == "openai"


@pytest.mark.asyncio
async def test_analyze_speech_success():
    client = OpenAIClient(api_key="test-key")
    
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"scores": {"overall": 8.5, "pronunciation": 9}, "feedback": {"conversational": "Tốt lắm!"}}'
    
    with patch.object(client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
        result = await client.analyze_speech(
            transcript="Hello world",
            prosody_features={"pitch": {"mean": 180}, "speaking_rate": {"syllables_per_second": 3.5}}
        )
        
        assert result["scores"]["overall"] == 8.5
        assert result["scores"]["pronunciation"] == 9
        assert "conversational" in result["feedback"]
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4o"


@pytest.mark.asyncio
async def test_analyze_speech_with_reference():
    client = OpenAIClient(api_key="test-key")
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"scores": {"overall": 7.5}, "feedback": {"conversational": "Cần cải thiện"}}'
    
    with patch.object(client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
        result = await client.analyze_speech(
            transcript="Hello",
            prosody_features={"pitch": {"mean": 150}},
            reference_text="Hello world",
            mode="sentence_practice"
        )
        
        assert result["scores"]["overall"] == 7.5
        mock_create.assert_called_once()
        
        # Verify reference text is in prompt
        call_args = mock_create.call_args
        messages = call_args.kwargs["messages"]
        assert any("Reference text:" in msg["content"] for msg in messages)


@pytest.mark.asyncio
async def test_analyze_speech_api_error():
    client = OpenAIClient(api_key="test-key")
    
    with patch.object(client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = Exception("API Error")
        
        with pytest.raises(LLMProviderError) as exc_info:
            await client.analyze_speech("Hello", {"pitch": {"mean": 180}})
        
        assert "OpenAI failed" in str(exc_info.value)
        assert exc_info.value.provider == "openai"


@pytest.mark.asyncio
async def test_health_check_success():
    client = OpenAIClient(api_key="test-key")
    
    with patch.object(client.client.models, 'list', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []
        
        result = await client.health_check()
        assert result is True


@pytest.mark.asyncio
async def test_health_check_failure():
    client = OpenAIClient(api_key="test-key")
    
    with patch.object(client.client.models, 'list', new_callable=AsyncMock) as mock_list:
        mock_list.side_effect = Exception("Connection error")
        
        result = await client.health_check()
        assert result is False
