"""Test API Sentences Endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.models.sentence import Sentence


class TestSentences:
    """Sentences endpoint tests"""
    
    def test_get_sentences_empty(self, client: TestClient):
        """Test get sentences when database is empty"""
        response = client.get("/api/v1/sentences")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total_items"] == 0
    
    def test_get_sentences_by_lesson(self, client: TestClient, test_sentences: list[Sentence]):
        """Test get sentences filtered by lesson"""
        lesson_id = test_sentences[0].lesson_id
        response = client.get(f"/api/v1/sentences?lesson_id={lesson_id}")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= len(test_sentences)
        assert all(item["lesson_id"] == lesson_id for item in data["items"])
    
    def test_get_sentence_by_id(self, client: TestClient, test_sentence: Sentence):
        """Test get specific sentence"""
        response = client.get(f"/api/v1/sentences/{test_sentence.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_sentence.id
        assert data["vi_text"] == test_sentence.vi_text
        assert data["en_text"] == test_sentence.en_text
        # Audio URLs may or may not be present depending on schema
        assert "lesson_id" in data
    
    def test_get_sentence_not_found(self, client: TestClient):
        """Test get non-existent sentence"""
        response = client.get("/api/v1/sentences/9999")
        assert response.status_code == 404
    
    def test_create_sentence_as_admin(self, client: TestClient, admin_token: str, test_lesson: Lesson):
        """Test create sentence as admin"""
        response = client.post(
            "/api/v1/sentences",
            json={
                "lesson_id": test_lesson.id,
                "vi_text": "Chào buổi sáng",
                "en_text": "Good morning",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["vi_text"] == "Chào buổi sáng"
        assert data["en_text"] == "Good morning"
        assert data["lesson_id"] == test_lesson.id
        assert "id" in data
    
    def test_create_sentence_with_invalid_lesson(self, client: TestClient, admin_token: str):
        """Test create sentence with non-existent lesson"""
        response = client.post(
            "/api/v1/sentences",
            json={
                "lesson_id": 9999,
                "vi_text": "Test",
                "en_text": "Test",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404
    
    def test_create_sentence_as_user(self, client: TestClient, user_token: str, test_lesson: Lesson):
        """Test create sentence as regular user fails"""
        response = client.post(
            "/api/v1/sentences",
            json={
                "lesson_id": test_lesson.id,
                "vi_text": "Test",
                "en_text": "Test",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 403
    
    def test_bulk_create_sentences(self, client: TestClient, admin_token: str, test_lesson: Lesson):
        """Test bulk create sentences"""
        response = client.post(
            "/api/v1/sentences/bulk",
            json={
                "lesson_id": test_lesson.id,
                "sentences": [
                    {"vi": "Một", "en": "One"},
                    {"vi": "Hai", "en": "Two"},
                    {"vi": "Ba", "en": "Three"},
                ],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        # Response is a list of created sentences
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["vi_text"] == "Một"
        assert data[2]["en_text"] == "Three"
    
    def test_bulk_create_empty_list(self, client: TestClient, admin_token: str, test_lesson: Lesson):
        """Test bulk create with empty list"""
        response = client.post(
            "/api/v1/sentences/bulk",
            json={
                "lesson_id": test_lesson.id,
                "sentences": [],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400
    
    def test_update_sentence(self, client: TestClient, admin_token: str, test_sentence: Sentence):
        """Test update sentence"""
        response = client.put(
            f"/api/v1/sentences/{test_sentence.id}",
            json={
                "vi_text": "Updated Vietnamese",
                "en_text": "Updated English",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["vi_text"] == "Updated Vietnamese"
        assert data["en_text"] == "Updated English"
    
    def test_update_sentence_lesson(self, client: TestClient, admin_token: str, test_sentence: Sentence, db: Session):
        """Test update sentence to different lesson"""
        # Create another lesson
        new_lesson = Lesson(title="New Lesson", order_index=2)
        db.add(new_lesson)
        db.commit()
        db.refresh(new_lesson)
        
        response = client.put(
            f"/api/v1/sentences/{test_sentence.id}",
            json={"lesson_id": new_lesson.id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["lesson_id"] == new_lesson.id
    
    def test_delete_sentence(self, client: TestClient, admin_token: str, test_sentence: Sentence):
        """Test delete sentence"""
        response = client.delete(
            f"/api/v1/sentences/{test_sentence.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/api/v1/sentences/{test_sentence.id}")
        assert get_response.status_code == 404
    
    def test_sentences_pagination(self, client: TestClient, admin_token: str, test_lesson: Lesson):
        """Test sentences pagination"""
        # Create 25 sentences
        for i in range(25):
            client.post(
                "/api/v1/sentences",
                json={
                    "lesson_id": test_lesson.id,
                    "vi_text": f"Câu {i+1}",
                    "en_text": f"Sentence {i+1}",
                },
                headers={"Authorization": f"Bearer {admin_token}"},
            )
        
        # Get first page
        response = client.get("/api/v1/sentences?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "pagination" in data
        assert data["pagination"]["total_items"] >= 25
        assert len(data["items"]) == 10
        assert data["pagination"]["total_pages"] == 3
