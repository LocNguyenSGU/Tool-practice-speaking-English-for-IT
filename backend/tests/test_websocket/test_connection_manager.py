import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from app.api.v1.websocket.connection_manager import ConnectionManager


@pytest.fixture
def manager():
    """Create a fresh ConnectionManager for each test"""
    return ConnectionManager()


@pytest.mark.asyncio
async def test_connect_accepts_websocket(manager):
    """Test that connect accepts the WebSocket and stores connection"""
    mock_websocket = AsyncMock()
    session_id = "test-session-123"
    
    await manager.connect(mock_websocket, session_id)
    
    # Verify websocket.accept() was called
    mock_websocket.accept.assert_called_once()
    
    # Verify connection is stored
    assert session_id in manager.active_connections
    assert manager.active_connections[session_id] == mock_websocket


@pytest.mark.asyncio
async def test_connect_initializes_session_data(manager):
    """Test that connect initializes session data structure"""
    mock_websocket = AsyncMock()
    session_id = "test-session-123"
    
    await manager.connect(mock_websocket, session_id)
    
    # Verify session data is initialized
    assert session_id in manager.session_data
    assert "audio_chunks" in manager.session_data[session_id]
    assert "start_time" in manager.session_data[session_id]
    assert isinstance(manager.session_data[session_id]["audio_chunks"], list)
    assert isinstance(manager.session_data[session_id]["start_time"], datetime)


def test_disconnect_removes_connection(manager):
    """Test that disconnect removes connection and session data"""
    # Setup
    mock_websocket = Mock()
    session_id = "test-session-123"
    manager.active_connections[session_id] = mock_websocket
    manager.session_data[session_id] = {"audio_chunks": [], "start_time": datetime.utcnow()}
    
    # Execute
    manager.disconnect(session_id)
    
    # Verify both are removed
    assert session_id not in manager.active_connections
    assert session_id not in manager.session_data


def test_disconnect_handles_nonexistent_session(manager):
    """Test that disconnect gracefully handles non-existent session"""
    # Should not raise error
    manager.disconnect("nonexistent-session")
    
    # Manager should remain empty
    assert len(manager.active_connections) == 0
    assert len(manager.session_data) == 0


@pytest.mark.asyncio
async def test_send_message_sends_json(manager):
    """Test that send_message sends JSON to the WebSocket"""
    mock_websocket = AsyncMock()
    session_id = "test-session-123"
    manager.active_connections[session_id] = mock_websocket
    
    message = {"type": "progress", "data": {"status": "processing"}}
    
    await manager.send_message(session_id, message)
    
    mock_websocket.send_json.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_send_message_ignores_nonexistent_session(manager):
    """Test that send_message ignores non-existent session without error"""
    message = {"type": "error", "data": "test"}
    
    # Should not raise error
    await manager.send_message("nonexistent-session", message)


@pytest.mark.asyncio
async def test_multiple_connections(manager):
    """Test managing multiple simultaneous connections"""
    sessions = ["session-1", "session-2", "session-3"]
    websockets = [AsyncMock() for _ in range(3)]
    
    # Connect all sessions
    for session_id, ws in zip(sessions, websockets):
        await manager.connect(ws, session_id)
    
    # Verify all are connected
    assert len(manager.active_connections) == 3
    assert len(manager.session_data) == 3
    
    # Disconnect one
    manager.disconnect("session-2")
    
    # Verify only that one is removed
    assert len(manager.active_connections) == 2
    assert "session-1" in manager.active_connections
    assert "session-2" not in manager.active_connections
    assert "session-3" in manager.active_connections


def test_get_session_data(manager):
    """Test getting session data"""
    session_id = "test-session-123"
    expected_data = {"audio_chunks": [b"chunk1"], "start_time": datetime.utcnow()}
    manager.session_data[session_id] = expected_data
    
    data = manager.get_session_data(session_id)
    
    assert data == expected_data


def test_get_session_data_nonexistent_returns_none(manager):
    """Test that getting non-existent session data returns None"""
    data = manager.get_session_data("nonexistent-session")
    
    assert data is None
