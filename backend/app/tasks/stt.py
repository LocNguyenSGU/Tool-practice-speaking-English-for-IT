from celery import Task
from app.core.celery_app import celery_app
import whisper
from functools import lru_cache
from typing import Dict, Any


@lru_cache(maxsize=2)
def get_whisper_model(model_size: str = "turbo"):
    """Load and cache Whisper model"""
    return whisper.load_model(model_size)


@celery_app.task(name='app.tasks.stt.transcribe_audio', queue='stt')
def transcribe_audio_task(audio_path: str, session_id: str) -> Dict[str, Any]:
    """
    Transcribe audio file using Whisper model
    
    Args:
        audio_path: Path to the audio file
        session_id: Session ID for tracking
    
    Returns:
        Dictionary containing transcription results
    """
    model = get_whisper_model("turbo")
    
    result = model.transcribe(
        audio_path,
        language="en",
        word_timestamps=True,
        fp16=False
    )
    
    # Calculate confidence from word-level probabilities
    confidence = _calculate_confidence(result)
    
    return {
        "text": result["text"],
        "segments": result["segments"],
        "confidence": confidence,
        "language": result.get("language", "en")
    }


def _calculate_confidence(result: Dict[str, Any]) -> float:
    """Calculate average confidence from word probabilities"""
    all_probs = []
    
    for segment in result.get("segments", []):
        for word in segment.get("words", []):
            if "probability" in word:
                all_probs.append(word["probability"])
    
    if not all_probs:
        return 0.9  # Default confidence if no probabilities available
    
    return sum(all_probs) / len(all_probs)
