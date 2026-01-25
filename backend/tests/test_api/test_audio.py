"""
Audio API endpoint tests
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.sentence import Sentence
from app.models.lesson import Lesson
from app.models.audio_file import AudioFile


class TestAudioAPI:
    """Test audio endpoints"""
    
    @patch('app.services.tts_service.TTSService.generate_audio')
    def test_get_audio_vietnamese(self, mock_generate, client: TestClient, db: Session, test_lesson: Lesson):
        """Test getting Vietnamese audio file"""
        # Create a test sentence
        sentence = Sentence(
            lesson_id=test_lesson.id,
            vi_text="Xin chào",
            en_text="Hello",
            order_index=1
        )
        db.add(sentence)
        db.commit()
        db.refresh(sentence)
        
        # Create temp audio file
        import tempfile
        import os
        temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.mp3', delete=False)
        temp_file.write(b'fake audio content')
        temp_file.close()
        
        # Mock audio generation to return temp file path
        mock_generate.return_value = temp_file.name
        
        try:
            response = client.get(f"/api/v1/audio/{sentence.id}/vi")
            
            assert response.status_code == 200
            assert mock_generate.called
            mock_generate.assert_called_with(sentence.id, "Xin chào", "vi")
        finally:
            # Cleanup temp file
            os.unlink(temp_file.name)
    
    @patch('app.services.tts_service.TTSService.generate_audio')
    def test_get_audio_english(self, mock_generate, client: TestClient, db: Session, test_lesson: Lesson):
        """Test getting English audio file"""
        sentence = Sentence(
            lesson_id=test_lesson.id,
            vi_text="Xin chào",
            en_text="Hello",
            order_index=1
        )
        db.add(sentence)
        db.commit()
        db.refresh(sentence)
        
        # Create temp audio file
        import tempfile
        import os
        temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.mp3', delete=False)
        temp_file.write(b'fake audio content')
        temp_file.close()
        
        mock_generate.return_value = temp_file.name
        
        try:
            response = client.get(f"/api/v1/audio/{sentence.id}/en")
            
            assert response.status_code == 200
            mock_generate.assert_called_with(sentence.id, "Hello", "en")
        finally:
            os.unlink(temp_file.name)
    
    def test_get_audio_sentence_not_found(self, client: TestClient):
        """Test getting audio for non-existent sentence"""
        response = client.get("/api/v1/audio/99999/vi")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data or "message" in data
    
    def test_get_audio_invalid_language(self, client: TestClient, db: Session, test_lesson: Lesson):
        """Test getting audio with invalid language code"""
        sentence = Sentence(
            lesson_id=test_lesson.id,
            vi_text="Xin chào",
            en_text="Hello",
            order_index=1
        )
        db.add(sentence)
        db.commit()
        
        response = client.get(f"/api/v1/audio/{sentence.id}/fr")
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.services.tts_service.TTSService.generate_audio')
    def test_get_audio_creates_record(self, mock_generate, client: TestClient, db: Session, test_lesson: Lesson):
        """Test that audio file record is created in database"""
        sentence = Sentence(
            lesson_id=test_lesson.id,
            vi_text="Test",
            en_text="Test",
            order_index=1
        )
        db.add(sentence)
        db.commit()
        db.refresh(sentence)
        
        # Create temp audio file
        import tempfile
        import os
        temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.mp3', delete=False)
        temp_file.write(b'fake audio content')
        temp_file.close()
        
        mock_generate.return_value = temp_file.name
        
        try:
            # First call - should create record
            response = client.get(f"/api/v1/audio/{sentence.id}/vi")
            assert response.status_code == 200
            
            # Check record was created
            audio_file = db.query(AudioFile).filter(
                AudioFile.sentence_id == sentence.id,
                AudioFile.language == "vi"
            ).first()
            
            assert audio_file is not None
            assert audio_file.file_path is not None
            assert audio_file.file_size is not None
            assert audio_file.file_size >= 0
        finally:
            os.unlink(temp_file.name)
    
    @patch('app.services.tts_service.TTSService.delete_audio')
    def test_delete_audio_cache(self, mock_delete, client: TestClient, db: Session, test_lesson: Lesson):
        """Test deleting audio cache"""
        sentence = Sentence(
            lesson_id=test_lesson.id,
            vi_text="Test",
            en_text="Test",
            order_index=1
        )
        db.add(sentence)
        db.commit()
        db.refresh(sentence)
        
        # Create audio file records
        audio_vi = AudioFile(
            sentence_id=sentence.id,
            language="vi",
            file_path="/tmp/test_vi.mp3",
            file_size=1024
        )
        audio_en = AudioFile(
            sentence_id=sentence.id,
            language="en",
            file_path="/tmp/test_en.mp3",
            file_size=2048
        )
        db.add_all([audio_vi, audio_en])
        db.commit()
        
        response = client.delete(f"/api/v1/audio/{sentence.id}")
        
        assert response.status_code == 200
        data = response.json()
        message = data.get("message", data.get("detail", "")).lower()
        assert "delete" in message or "success" in message
        mock_delete.assert_called_with(sentence.id)
        
        # Check records were deleted
        audio_count = db.query(AudioFile).filter(
            AudioFile.sentence_id == sentence.id
        ).count()
        assert audio_count == 0
    
    def test_delete_audio_cache_sentence_not_found(self, client: TestClient):
        """Test deleting audio cache for non-existent sentence"""
        response = client.delete("/api/v1/audio/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data or "message" in data
