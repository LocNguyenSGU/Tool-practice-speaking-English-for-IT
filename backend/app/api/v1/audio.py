"""
Audio Endpoints
"""
from fastapi import APIRouter, Depends, Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.sentence import Sentence
from app.models.audio_file import AudioFile
from app.services.tts_service import TTSService
from app.dependencies import get_optional_user

router = APIRouter()


@router.get("/audio/{sentence_id}/{language}")
async def get_audio(
    sentence_id: int = Path(..., description="Sentence ID"),
    language: str = Path(..., pattern="^(vi|en)$", description="Language: 'vi' or 'en'"),
    user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Get audio file for a sentence
    - **sentence_id**: Sentence ID
    - **language**: Language code ('vi' or 'en')
    
    Public endpoint (guest + registered users)
    
    Returns: MP3 audio file
    
    Note: Audio is generated on-demand if not exists and cached for future requests
    """
    # Get sentence
    sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
    if not sentence:
        raise NotFoundException(f"Sentence with id {sentence_id} not found")
    
    # Get text based on language
    text = sentence.vi_text if language == "vi" else sentence.en_text
    
    # Generate audio (or get cached)
    tts = TTSService()
    audio_path = tts.generate_audio(text, language, sentence_id)
    
    # Check if AudioFile record exists, create if not
    audio_file = (
        db.query(AudioFile)
        .filter(AudioFile.sentence_id == sentence_id, AudioFile.language == language)
        .first()
    )
    
    if not audio_file:
        # Get file size
        import os
        file_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
        
        audio_file = AudioFile(
            sentence_id=sentence_id,
            language=language,
            file_path=audio_path,
            file_size=file_size,
        )
        db.add(audio_file)
        db.commit()
    
    # Return audio file
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=f"sentence_{sentence_id}_{language}.mp3",
    )


@router.delete("/audio/{sentence_id}")
async def delete_audio_cache(
    sentence_id: int = Path(..., description="Sentence ID"),
    db: Session = Depends(get_db),
):
    """
    Delete cached audio files for a sentence
    
    This is a public endpoint to allow cache invalidation
    
    Use case: When sentence text is updated
    """
    # Check sentence exists
    sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
    if not sentence:
        raise NotFoundException(f"Sentence with id {sentence_id} not found")
    
    # Delete audio files
    TTSService.delete_audio(sentence_id)
    
    # Delete AudioFile records
    db.query(AudioFile).filter(AudioFile.sentence_id == sentence_id).delete()
    db.commit()
    
    return {"message": f"Audio cache for sentence {sentence_id} deleted"}
