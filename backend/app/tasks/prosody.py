from app.core.celery_app import celery_app
import librosa
import parselmouth
import numpy as np
from typing import Dict, Any


@celery_app.task(name='app.tasks.prosody.extract_features', queue='prosody')
def extract_prosody_task(audio_path: str, session_id: str) -> Dict[str, Any]:
    """
    Extract prosody features from audio file
    
    Args:
        audio_path: Path to the audio file
        session_id: Session ID for tracking
    
    Returns:
        Dictionary containing prosody features (pitch, energy, speaking rate)
    """
    # Load audio with librosa
    y, sr = librosa.load(audio_path, sr=16000)
    
    # Load with parselmouth for pitch analysis
    snd = parselmouth.Sound(audio_path)
    
    # Extract pitch features
    pitch = snd.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    pitch_values = pitch_values[pitch_values > 0]  # Filter out unvoiced frames
    
    # Extract energy (RMS)
    rms = librosa.feature.rms(y=y)[0]
    
    # Calculate speaking rate (syllables per second)
    speaking_rate = _calculate_speaking_rate(snd)
    
    # Build result
    if len(pitch_values) > 0:
        pitch_mean = float(np.mean(pitch_values))
        pitch_std = float(np.std(pitch_values))
    else:
        # No pitch detected (silence or noise)
        pitch_mean = 0.0
        pitch_std = 0.0
    
    return {
        "pitch": {
            "mean": pitch_mean,
            "std": pitch_std
        },
        "energy": {
            "mean": float(np.mean(rms)),
            "max": float(np.max(rms))
        },
        "speaking_rate": speaking_rate
    }


def _calculate_speaking_rate(sound: parselmouth.Sound) -> Dict[str, float]:
    """
    Calculate speaking rate from intensity peaks (syllable nuclei)
    
    Args:
        sound: Parselmouth Sound object
    
    Returns:
        Dictionary with syllables_per_second
    """
    duration = sound.get_total_duration()
    
    if duration == 0:
        return {"syllables_per_second": 0.0}
    
    # Extract intensity
    intensity = sound.to_intensity()
    intensity_values = intensity.values[0]
    
    # Count intensity peaks above threshold (syllable nuclei)
    threshold = np.mean(intensity_values) + 0.5 * np.std(intensity_values)
    peaks = _count_peaks(intensity_values, threshold)
    
    syllables_per_second = peaks / duration if duration > 0 else 0.0
    
    return {
        "syllables_per_second": float(syllables_per_second),
        "total_syllables": int(peaks)
    }


def _count_peaks(values: np.ndarray, threshold: float) -> int:
    """Count peaks above threshold in signal"""
    above_threshold = values > threshold
    
    # Count transitions from below to above threshold
    peaks = 0
    was_below = True
    
    for is_above in above_threshold:
        if is_above and was_below:
            peaks += 1
            was_below = False
        elif not is_above:
            was_below = True
    
    return peaks
