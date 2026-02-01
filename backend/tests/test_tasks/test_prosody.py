import pytest
from unittest.mock import patch, Mock, MagicMock
import numpy as np
from app.tasks.prosody import extract_prosody_task


def test_extract_prosody_task():
    """Test the extract_prosody_task with mocked librosa and parselmouth"""
    with patch('app.tasks.prosody.librosa') as mock_librosa, \
         patch('app.tasks.prosody.parselmouth') as mock_parselmouth:
        
        # Mock librosa
        mock_audio = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        mock_librosa.load.return_value = (mock_audio, 16000)
        mock_librosa.feature.rms.return_value = np.array([[0.1, 0.2, 0.15]])
        
        # Mock parselmouth Sound
        mock_sound = MagicMock()
        mock_parselmouth.Sound.return_value = mock_sound
        mock_sound.get_total_duration.return_value = 2.5
        
        # Mock pitch extraction
        mock_pitch = MagicMock()
        mock_pitch.selected_array = {
            'frequency': np.array([100.0, 120.0, 0.0, 110.0, 130.0])  # 0 indicates unvoiced
        }
        mock_sound.to_pitch.return_value = mock_pitch
        
        # Mock intensity extraction
        mock_intensity = MagicMock()
        mock_intensity.values = np.array([[0.5, 0.7, 0.6, 0.8, 0.9, 0.4, 0.5]])
        mock_sound.to_intensity.return_value = mock_intensity
        
        # Execute task
        result = extract_prosody_task("/tmp/test.wav", "session-123")
        
        # Assertions
        assert "pitch" in result
        assert "energy" in result
        assert "speaking_rate" in result
        assert result["pitch"]["mean"] > 0
        assert result["pitch"]["std"] >= 0
        assert result["energy"]["mean"] > 0


def test_extract_prosody_handles_no_pitch():
    """Test that prosody extraction handles audio with no detectable pitch"""
    with patch('app.tasks.prosody.librosa') as mock_librosa, \
         patch('app.tasks.prosody.parselmouth') as mock_parselmouth:
        
        # Mock audio with no pitch
        mock_audio = np.array([0.01, 0.02, 0.01])
        mock_librosa.load.return_value = (mock_audio, 16000)
        mock_librosa.feature.rms.return_value = np.array([[0.01]])
        
        mock_sound = MagicMock()
        mock_parselmouth.Sound.return_value = mock_sound
        mock_sound.get_total_duration.return_value = 1.0
        
        # All zeros = no pitch detected
        mock_pitch = MagicMock()
        mock_pitch.selected_array = {'frequency': np.array([0.0, 0.0, 0.0])}
        mock_sound.to_pitch.return_value = mock_pitch
        
        # Mock intensity
        mock_intensity = MagicMock()
        mock_intensity.values = np.array([[0.1, 0.1, 0.1]])
        mock_sound.to_intensity.return_value = mock_intensity
        
        result = extract_prosody_task("/tmp/test.wav", "session-123")
        
        # Should handle gracefully with default values
        assert result["pitch"]["mean"] == 0.0
        assert result["pitch"]["std"] == 0.0


def test_extract_prosody_calculates_speaking_rate():
    """Test that speaking rate is calculated"""
    with patch('app.tasks.prosody.librosa') as mock_librosa, \
         patch('app.tasks.prosody.parselmouth') as mock_parselmouth:
        
        # 5 seconds of audio at 16kHz
        audio_duration = 5.0
        mock_audio = np.random.randn(int(16000 * audio_duration))
        mock_librosa.load.return_value = (mock_audio, 16000)
        mock_librosa.feature.rms.return_value = np.array([[0.1] * 100])
        
        mock_sound = MagicMock()
        mock_parselmouth.Sound.return_value = mock_sound
        mock_sound.get_total_duration.return_value = audio_duration
        
        mock_pitch = MagicMock()
        mock_pitch.selected_array = {'frequency': np.array([100.0] * 100)}
        mock_sound.to_pitch.return_value = mock_pitch
        
        # Mock syllable nuclei detection - create pattern with peaks
        intensity_values = np.array([0.3, 0.8, 0.3, 0.9, 0.3, 0.85, 0.3, 0.9, 0.3, 0.8])
        mock_intensity = MagicMock()
        mock_intensity.values = np.array([intensity_values])
        mock_sound.to_intensity.return_value = mock_intensity
        
        result = extract_prosody_task("/tmp/test.wav", "session-123")
        
        assert "speaking_rate" in result
        assert "syllables_per_second" in result["speaking_rate"]
        assert result["speaking_rate"]["syllables_per_second"] > 0
