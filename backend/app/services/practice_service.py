from datetime import datetime, timedelta
from typing import Optional
import random
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.sentence import Sentence
from app.models.progress import UserProgress
from app.models.user import User
from app.core.exceptions import NotFoundException


class PracticeService:
    @staticmethod
    def get_next_sentence(
        db: Session,
        lesson_id: int,
        mode: str = "random",
        user: Optional[User] = None
    ) -> tuple[Sentence, Optional[dict]]:
        """Get next sentence for practice."""
        query = db.query(Sentence).filter(Sentence.lesson_id == lesson_id)
        
        if user:
            # Filter out recently practiced (< 5 minutes ago)
            recent_time = datetime.utcnow() - timedelta(minutes=5)
            recent_ids = db.query(UserProgress.sentence_id).filter(
                UserProgress.user_id == user.id,
                UserProgress.last_practiced_at > recent_time
            ).all()
            recent_ids = [r[0] for r in recent_ids]
            
            if recent_ids:
                query = query.filter(~Sentence.id.in_(recent_ids))
            
            # Prioritize least practiced
            sentences = query.all()
            if not sentences:
                # All practiced recently, just get any
                sentences = db.query(Sentence).filter(
                    Sentence.lesson_id == lesson_id
                ).all()
            
            if not sentences:
                raise NotFoundException("No sentences found in this lesson")
            
            # Get practice counts
            practice_counts = {}
            for s in sentences:
                count = db.query(UserProgress).filter(
                    UserProgress.user_id == user.id,
                    UserProgress.sentence_id == s.id
                ).first()
                practice_counts[s.id] = count.practiced_count if count else 0
            
            # Sort by practice count and pick randomly from least practiced
            sentences.sort(key=lambda x: practice_counts[x.id])
            min_count = practice_counts[sentences[0].id]
            least_practiced = [s for s in sentences if practice_counts[s.id] == min_count]
            sentence = random.choice(least_practiced)
            
            # Get progress info
            total_in_lesson = db.query(Sentence).filter(
                Sentence.lesson_id == lesson_id
            ).count()
            practiced_count = db.query(UserProgress).filter(
                UserProgress.user_id == user.id,
                UserProgress.sentence_id.in_(
                    db.query(Sentence.id).filter(Sentence.lesson_id == lesson_id)
                )
            ).count()
            
            progress = {
                "practiced_count": practice_counts[sentence.id],
                "total_in_lesson": total_in_lesson,
                "completion_percentage": round((practiced_count / total_in_lesson) * 100, 2) if total_in_lesson > 0 else 0
            }
            
            return sentence, progress
        else:
            # Guest mode - just random
            sentences = query.all()
            if not sentences:
                raise NotFoundException("No sentences found in this lesson")
            
            sentence = random.choice(sentences)
            return sentence, None
    
    @staticmethod
    def record_practice(db: Session, user: User, sentence_id: int):
        """Record that user practiced a sentence."""
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.sentence_id == sentence_id
        ).first()
        
        if progress:
            progress.practiced_count += 1
            progress.last_practiced_at = datetime.utcnow()
        else:
            progress = UserProgress(
                user_id=user.id,
                sentence_id=sentence_id,
                practiced_count=1,
                last_practiced_at=datetime.utcnow()
            )
            db.add(progress)
        
        db.commit()
