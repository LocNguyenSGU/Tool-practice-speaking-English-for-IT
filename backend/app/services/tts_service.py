import os
from pathlib import Path
from gtts import gTTS
import pyttsx3
from app.config import settings
from app.core.exceptions import BadRequestException


class TTSService:
    def __init__(self, audio_dir: str = None, engine: str = None):
        self.audio_dir = audio_dir or settings.audio_dir
        self.engine = engine or settings.tts_engine
        
        # Create audio directory if not exists
        Path(self.audio_dir).mkdir(parents=True, exist_ok=True)
    
    def get_audio_path(self, sentence_id: int, language: str) -> str:
        """Get audio file path for sentence and language."""
        extension = "mp3" if self.engine == "gtts" else "wav"
        return os.path.join(self.audio_dir, f"{sentence_id}_{language}.{extension}")
    
    def generate_audio(self, text: str, language: str, sentence_id: int) -> str:
        """Generate audio file for text."""
        file_path = self.get_audio_path(sentence_id, language)
        
        # Skip if already exists
        if os.path.exists(file_path):
            return file_path
        
        try:
            if self.engine == "gtts":
                self._generate_gtts(text, language, file_path)
            else:
                self._generate_pyttsx3(text, language, file_path)
            
            return file_path
        except Exception as e:
            raise BadRequestException(f"Failed to generate audio: {str(e)}")
    
    def _generate_gtts(self, text: str, language: str, file_path: str):
        """Generate audio using gTTS."""
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(file_path)
    
    def _generate_pyttsx3(self, text: str, language: str, file_path: str):
        """Generate audio using pyttsx3 (offline)."""
        engine = pyttsx3.init()
        
        # Set voice based on language
        voices = engine.getProperty('voices')
        if language == "vi":
            # Try to find Vietnamese voice
            for voice in voices:
                if "vietnamese" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
        else:
            # Default to first English voice
            engine.setProperty('voice', voices[0].id)
        
        engine.save_to_file(text, file_path)
        engine.runAndWait()
    
    def delete_audio(self, sentence_id: int, language: str = None):
        """Delete audio file(s) for sentence."""
        if language:
            file_path = self.get_audio_path(sentence_id, language)
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            # Delete both languages
            for lang in ["vi", "en"]:
                self.delete_audio(sentence_id, lang)
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        return os.path.getsize(file_path) if os.path.exists(file_path) else 0
