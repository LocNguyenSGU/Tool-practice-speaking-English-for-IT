"""Test API Lessons Endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.lesson import Lesson


class TestLessons:
    """Lessons endpoint tests"""
    
    def test_get_lessons_empty(self, client: TestClient):
        """Test get lessons when database is empty"""
        response = client.get("/api/v1/lessons")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total_items"] == 0
        assert data["items"] == []
    
    def test_get_lessons_with_data(self, client: TestClient, test_lesson: Lesson):
        """Test get lessons with data"""
        response = client.get("/api/v1/lessons")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total_items"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == test_lesson.title
    
    def test_get_lessons_pagination(self, client: TestClient, admin_token: str):
        """Test lessons pagination"""
        # Create 15 lessons
        for i in range(15):
            client.post(
                "/api/v1/lessons",
                json={"title": f"Lesson {i+1}", "description": f"Desc {i+1}"},
                headers={"Authorization": f"Bearer {admin_token}"},
            )
        
        # Get first page
        response = client.get("/api/v1/lessons?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total_items"] == 15
        assert len(data["items"]) == 10
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["total_pages"] == 2
        assert data["pagination"]["has_next"] is True
        assert data["pagination"]["has_prev"] is False
        
        # Get second page
        response = client.get("/api/v1/lessons?page=2&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["pagination"]["has_next"] is False
        assert data["pagination"]["has_prev"] is True
    
    def test_get_lessons_search(self, client: TestClient, admin_token: str):
        """Test lessons search"""
        # Create lessons with different titles
        client.post(
            "/api/v1/lessons",
            json={"title": "Greetings", "description": "Basic greetings"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        client.post(
            "/api/v1/lessons",
            json={"title": "Numbers", "description": "Count numbers"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        # Search for "greet"
        response = client.get("/api/v1/lessons?search=greet")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total_items"] == 1
        assert "Greetings" in data["items"][0]["title"]
    
    def test_get_lesson_by_id(self, client: TestClient, test_lesson: Lesson):
        """Test get specific lesson"""
        response = client.get(f"/api/v1/lessons/{test_lesson.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_lesson.id
        assert data["title"] == test_lesson.title
        # sentence_count may or may not be present
        if "sentence_count" in data:
            assert isinstance(data["sentence_count"], int)
    
    def test_get_lesson_not_found(self, client: TestClient):
        """Test get non-existent lesson"""
        response = client.get("/api/v1/lessons/9999")
        assert response.status_code == 404
        data = response.json()
        error_msg = data.get("detail", data.get("message", "")).lower()
        assert "not found" in error_msg
    
    def test_create_lesson_as_admin(self, client: TestClient, admin_token: str):
        """Test create lesson as admin"""
        response = client.post(
            "/api/v1/lessons",
            json={
                "title": "New Lesson",
                "description": "New Description",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Lesson"
        assert data["description"] == "New Description"
        assert "id" in data
        # order_index may be set automatically
    
    def test_create_lesson_as_user(self, client: TestClient, user_token: str):
        """Test create lesson as regular user fails"""
        response = client.post(
            "/api/v1/lessons",
            json={"title": "New Lesson"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 403
    
    def test_create_lesson_unauthorized(self, client: TestClient):
        """Test create lesson without authentication"""
        response = client.post(
            "/api/v1/lessons",
            json={"title": "New Lesson"},
        )
        assert response.status_code == 401
    
    def test_create_lesson_invalid_data(self, client: TestClient, admin_token: str):
        """Test create lesson with missing required fields"""
        response = client.post(
            "/api/v1/lessons",
            json={"description": "Only description"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 422
    
    def test_update_lesson(self, client: TestClient, admin_token: str, test_lesson: Lesson):
        """Test update lesson"""
        response = client.put(
            f"/api/v1/lessons/{test_lesson.id}",
            json={
                "title": "Updated Title",
                "description": "Updated Description",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated Description"
    
    def test_update_lesson_as_user(self, client: TestClient, user_token: str, test_lesson: Lesson):
        """Test update lesson as regular user fails"""
        response = client.put(
            f"/api/v1/lessons/{test_lesson.id}",
            json={"title": "Updated"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 403
    
    def test_update_lesson_not_found(self, client: TestClient, admin_token: str):
        """Test update non-existent lesson"""
        response = client.put(
            "/api/v1/lessons/9999",
            json={"title": "Updated"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404
    
    def test_delete_lesson(self, client: TestClient, admin_token: str, test_lesson: Lesson):
        """Test delete lesson"""
        response = client.delete(
            f"/api/v1/lessons/{test_lesson.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/api/v1/lessons/{test_lesson.id}")
        assert get_response.status_code == 404
    
    def test_delete_lesson_as_user(self, client: TestClient, user_token: str, test_lesson: Lesson):
        """Test delete lesson as regular user fails"""
        response = client.delete(
            f"/api/v1/lessons/{test_lesson.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 403
    
    def test_delete_lesson_cascade(self, client: TestClient, admin_token: str, test_lesson: Lesson, test_sentence):
        """Test delete lesson also deletes sentences"""
        lesson_id = test_lesson.id
        
        # Delete lesson
        response = client.delete(
            f"/api/v1/lessons/{lesson_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204
        
        # Verify sentences also deleted
        sentences_response = client.get(f"/api/v1/sentences?lesson_id={lesson_id}")
        assert sentences_response.json()["pagination"]["total_items"] == 0
