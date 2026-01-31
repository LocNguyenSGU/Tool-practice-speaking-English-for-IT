"""
Tests for Practice Service
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.practice_service import PracticeService
from app.models.sentence import Sentence
from app.models.lesson import Lesson
from app.models.user import User
from app.models.progress import UserProgress
from app.core.exceptions import NotFoundException


class TestPracticeService:
    """Test practice service smart algorithm"""
    
    def test_get_next_sentence_random_no_user(self, db: Session, test_lesson: Lesson, test_sentences: list[Sentence]):
        """Test getting random sentence without user"""
        sentence, suggestion = PracticeService.get_next_sentence(
            db, test_lesson.id, mode="random", user=None
        )
        assert sentence is not None
        assert sentence.lesson_id == test_lesson.id
        assert suggestion is not None
        assert suggestion["practiced_count"] == 0
    
    def test_get_next_sentence_with_user_no_history(self, db: Session, test_user: User, test_lesson: Lesson, test_sentences: list[Sentence]):
        """Test getting sentence for user with no practice history"""
        sentence, suggestion = PracticeService.get_next_sentence(
            db, test_lesson.id, mode="smart", user=test_user
        )
        assert sentence is not None
        assert sentence.lesson_id == test_lesson.id
        # Should suggest least practiced (all are 0)
        assert suggestion is not None
    
    def test_get_next_sentence_filters_recent(self, db: Session, test_user: User, test_lesson: Lesson, test_sentences: list[Sentence]):
        """Test that recently practiced sentences are filtered out"""
        # Practice first sentence recently (< 5 min ago)
        recent_progress = UserProgress(
            user_id=test_user.id,
            sentence_id=test_sentences[0].id,
            practiced_count=1,
            last_practiced_at=datetime.utcnow() - timedelta(minutes=2)
        )
        db.add(recent_progress)
        db.commit()
        
        sentence, _ = PracticeService.get_next_sentence(
            db, test_lesson.id, mode="smart", user=test_user
        )
        
        # Should not get the recently practiced one
        assert sentence.id != test_sentences[0].id
    
    def test_get_next_sentence_prioritizes_least_practiced(self, db: Session, test_user: User, test_lesson: Lesson, test_sentences: list[Sentence]):
        """Test that least practiced sentences are prioritized"""
        # Practice some sentences more than others
        for i, sent in enumerate(test_sentences[:2]):
            progress = UserProgress(
                user_id=test_user.id,
                sentence_id=sent.id,
                practiced_count=i + 5,  # 5, 6
                last_practiced_at=datetime.utcnow() - timedelta(hours=1)
            )
            db.add(progress)
        db.commit()
        
        # Should get one of the unpracticed sentences (index 2+)
        sentence, progress_info = PracticeService.get_next_sentence(
            db, test_lesson.id, mode="smart", user=test_user
        )
        
        assert sentence.id in [s.id for s in test_sentences[2:]]
        assert progress_info is not None
        assert progress_info["practiced_count"] == 2  # 2 unique sentences practiced in this lesson
    
    def test_record_practice_creates_new_progress(self, db: Session, test_user: User, test_sentences: list[Sentence]):
        """Test recording practice creates new progress record"""
        sentence = test_sentences[0]
        PracticeService.record_practice(db, user=test_user, sentence_id=sentence.id)
        
        # Check progress was created
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == test_user.id,
            UserProgress.sentence_id == sentence.id
        ).first()
        
        assert progress is not None
        assert progress.user_id == test_user.id
        assert progress.sentence_id == sentence.id
        assert progress.practiced_count == 1
    
    def test_record_practice_updates_existing(self, db: Session, test_user: User, test_sentences: list[Sentence]):
        """Test recording practice updates existing progress"""
        sentence = test_sentences[0]
        
        # Create initial progress
        progress = UserProgress(
            user_id=test_user.id,
            sentence_id=sentence.id,
            practiced_count=3,
            last_practiced_at=datetime.utcnow() - timedelta(hours=1)
        )
        db.add(progress)
        db.commit()
        
        # Record another practice
        PracticeService.record_practice(db, user=test_user, sentence_id=sentence.id)
        db.refresh(progress)
        
        assert progress.practiced_count == 4
    
    def test_get_next_sentence_no_sentences_found(self, db: Session, test_user: User):
        """Test getting sentence when none exist in lesson"""
        with pytest.raises(NotFoundException):
            PracticeService.get_next_sentence(db, lesson_id=99999, user=test_user)
