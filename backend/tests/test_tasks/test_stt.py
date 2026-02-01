import pytest
from unittest.mock import patch, Mock
from app.tasks.stt import transcribe_audio_task, get_whisper_model


def test_transcribe_audio_task():
    """Test the transcribe_audio_task with mocked Whisper model"""
    with patch('app.tasks.stt.get_whisper_model') as mock_model:
        # Setup mock model
        model = Mock()
        model.transcribe.return_value = {
            "text": "Hello world",
            "segments": [
                {
                    "text": "Hello world",
                    "start": 0.0,
                    "end": 1.5,
                    "words": [
                        {"word": "Hello", "start": 0.0, "end": 0.5, "probability": 0.95},
                        {"word": "world", "start": 0.6, "end": 1.5, "probability": 0.98}
                    ]
                }
            ],
            "language": "en"
        }
        mock_model.return_value = model
        
        # Execute task
        result = transcribe_audio_task("/tmp/test.wav", "session-123")
        
        # Assertions
        assert result["text"] == "Hello world"
        assert "confidence" in result
        assert result["confidence"] > 0.9
        assert "segments" in result
        assert len(result["segments"]) == 1


def test_transcribe_audio_task_calculates_confidence():
    """Test that confidence is calculated from word probabilities"""
    with patch('app.tasks.stt.get_whisper_model') as mock_model:
        model = Mock()
        model.transcribe.return_value = {
            "text": "Test",
            "segments": [
                {
                    "words": [
                        {"word": "Test", "probability": 0.85}
                    ]
                }
            ],
            "language": "en"
        }
        mock_model.return_value = model
        
        result = transcribe_audio_task("/tmp/test.wav", "session-123")
        
        # Confidence should be calculated from probabilities
        assert result["confidence"] == pytest.approx(0.85, 0.01)


def test_get_whisper_model_caching():
    """Test that get_whisper_model caches the model"""
    with patch('whisper.load_model') as mock_load:
        mock_model = Mock()
        mock_load.return_value = mock_model
        
        # Clear cache
        get_whisper_model.cache_clear()
        
        # First call should load model
        model1 = get_whisper_model("turbo")
        assert mock_load.call_count == 1
        
        # Second call should use cache
        model2 = get_whisper_model("turbo")
        assert mock_load.call_count == 1  # Still 1, not 2
        
        assert model1 is model2
