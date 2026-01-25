"""Test TTS Service"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.services.tts_service import TTSService
from app.core.exceptions import BadRequestException


class TestTTSService:
    """Test TTS Service"""
    
    @pytest.fixture
    def temp_audio_dir(self):
        """Create temporary audio directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def tts_service(self, temp_audio_dir):
        """Create TTS service with temp directory"""
        return TTSService(audio_dir=temp_audio_dir, engine="gtts")
    
    def test_init_creates_directory(self, temp_audio_dir):
        """Test service creates audio directory"""
        audio_dir = os.path.join(temp_audio_dir, "new_audio")
        service = TTSService(audio_dir=audio_dir)
        
        assert os.path.exists(audio_dir)
        assert os.path.isdir(audio_dir)
    
    def test_get_audio_path(self, tts_service, temp_audio_dir):
        """Test audio path generation"""
        path = tts_service.get_audio_path(123, "vi")
        
        assert temp_audio_dir in path
        assert "123_vi.mp3" in path
    
    def test_get_audio_path_english(self, tts_service):
        """Test audio path for English"""
        path = tts_service.get_audio_path(456, "en")
        assert "456_en.mp3" in path
    
    @patch('app.services.tts_service.gTTS')
    def test_generate_audio_success(self, mock_gtts, tts_service):
        """Test audio generation success"""
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        
        file_path = tts_service.generate_audio("Hello", "en", 1)
        
        # Verify gTTS called
        mock_gtts.assert_called_once_with(text="Hello", lang="en", slow=False)
        mock_tts_instance.save.assert_called_once()
        assert file_path.endswith("1_en.mp3")
    
    @patch('app.services.tts_service.gTTS')
    def test_generate_audio_vietnamese(self, mock_gtts, tts_service):
        """Test Vietnamese audio generation"""
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        
        tts_service.generate_audio("Xin chào", "vi", 2)
        
        mock_gtts.assert_called_once_with(text="Xin chào", lang="vi", slow=False)
    
    @patch('app.services.tts_service.gTTS')
    def test_generate_audio_skips_existing(self, mock_gtts, tts_service):
        """Test skips generation if file exists"""
        # Create dummy file
        file_path = tts_service.get_audio_path(3, "en")
        Path(file_path).touch()
        
        result = tts_service.generate_audio("Test", "en", 3)
        
        # Should not call gTTS
        mock_gtts.assert_not_called()
        assert result == file_path
    
    @patch('app.services.tts_service.gTTS')
    def test_generate_audio_handles_error(self, mock_gtts, tts_service):
        """Test handles generation error"""
        mock_gtts.side_effect = Exception("TTS Error")
        
        with pytest.raises(BadRequestException) as exc_info:
            tts_service.generate_audio("Test", "en", 4)
        
        assert "Failed to generate audio" in str(exc_info.value.detail)
    
    def test_delete_audio(self, tts_service):
        """Test audio file deletion"""
        # Create dummy file
        file_path = tts_service.get_audio_path(5, "vi")
        Path(file_path).touch()
        
        assert os.path.exists(file_path)
        
        tts_service.delete_audio(5, "vi")
        
        assert not os.path.exists(file_path)
    
    def test_delete_audio_both_languages(self, tts_service):
        """Test deleting audio for both languages"""
        # Create dummy files
        vi_path = tts_service.get_audio_path(6, "vi")
        en_path = tts_service.get_audio_path(6, "en")
        Path(vi_path).touch()
        Path(en_path).touch()
        
        tts_service.delete_audio(6)
        
        assert not os.path.exists(vi_path)
        assert not os.path.exists(en_path)
