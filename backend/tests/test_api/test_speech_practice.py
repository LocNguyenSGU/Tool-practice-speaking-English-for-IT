import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.speech_practice import SpeechPracticeSession


def test_create_session(client: TestClient, test_user, user_token, db: Session):
    """Test creating a new speech practice session"""
    response = client.post(
        "/api/v1/speech-practice/sessions",
        json={"mode": "conversation"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["mode"] == "conversation"
    assert data["status"] == "in_progress"
    assert data["user_id"] == str(test_user.id)
    assert data["reference_text"] is None


def test_create_session_sentence_mode(client: TestClient, test_user, test_sentence, user_token, db: Session):
    """Test creating a session in sentence practice mode"""
    response = client.post(
        "/api/v1/speech-practice/sessions",
        json={
            "mode": "sentence_practice",
            "reference_text": test_sentence.en_text
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "sentence_practice"
    assert data["reference_text"] == test_sentence.en_text


def test_create_session_requires_auth(client: TestClient):
    """Test that creating a session requires authentication"""
    response = client.post(
        "/api/v1/speech-practice/sessions",
        json={"mode": "conversation"}
    )
    
    assert response.status_code == 401


def test_create_session_invalid_mode(client: TestClient, user_token):
    """Test that invalid mode is rejected"""
    response = client.post(
        "/api/v1/speech-practice/sessions",
        json={"mode": "invalid_mode"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    
    assert response.status_code == 422



def test_get_session(client: TestClient, test_user, user_token, db: Session):
    """Test getting session details"""
    # First create a session
    create_response = client.post(
        "/api/v1/speech-practice/sessions",
        json={"mode": "conversation"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    session_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(
        f"/api/v1/speech-practice/sessions/{session_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["mode"] == "conversation"
    assert data["user_id"] == str(test_user.id)


def test_get_session_not_found(client: TestClient, user_token):
    """Test getting non-existent session returns 404"""
    import uuid
    fake_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/speech-practice/sessions/{fake_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    
    assert response.status_code == 404


def test_get_session_unauthorized(client: TestClient, test_user, test_admin, user_token, admin_token, db: Session):
    """Test that users can't access other users' sessions"""
    # Create session with regular user
    create_response = client.post(
        "/api/v1/speech-practice/sessions",
        json={"mode": "conversation"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    session_id = create_response.json()["id"]
    
    # Try to access with different user (admin)
    response = client.get(
        f"/api/v1/speech-practice/sessions/{session_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    # Should return 403 or 404 depending on implementation
    assert response.status_code in [403, 404]


def test_list_user_sessions(client: TestClient, test_user, user_token, db: Session):
    """Test listing all sessions for current user"""
    # Create multiple sessions
    # Create 3 sessions
    for i in range(3):
        client.post(
            "/api/v1/speech-practice/sessions",
            json={"mode": "conversation"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
    
    # List sessions
    response = client.get(
        "/api/v1/speech-practice/sessions",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert len(data["sessions"]) >= 3


def test_update_session_results(client: TestClient, test_user, user_token, db: Session):
    """Test updating session with results"""
    # Create session
    create_response = client.post(
        "/api/v1/speech-practice/sessions",
        json={"mode": "conversation"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    session_id = create_response.json()["id"]
    
    # Update with results
    results = {
        "transcript": "Hello world",
        "scores": {
            "overall": 8.5,
            "pronunciation": 9.0,
            "prosody": 8.0
        },
        "feedback": {
            "conversational": "Good job!",
            "detailed": {"strengths": ["Clear pronunciation"]}
        }
    }
    
    response = client.put(
        f"/api/v1/speech-practice/sessions/{session_id}/results",
        json=results,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_delete_session(client: TestClient, test_user, user_token, db: Session):
    """Test deleting a session"""
    # Create session
    create_response = client.post(
        "/api/v1/speech-practice/sessions",
        json={"mode": "conversation"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    session_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(
        f"/api/v1/speech-practice/sessions/{session_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    
    assert response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(
        f"/api/v1/speech-practice/sessions/{session_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert get_response.status_code == 404
