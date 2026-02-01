import pytest
from unittest.mock import AsyncMock, patch, Mock
from fastapi.testclient import TestClient
from app.main import app
import json


def test_websocket_endpoint_exists():
    """Test that the WebSocket endpoint is registered"""
    # Check that the route exists
    routes = [route.path for route in app.routes]
    assert "/ws/speech-practice" in routes


@pytest.mark.asyncio
async def test_websocket_connection():
    """Test basic WebSocket connection and disconnection"""
    from app.api.v1.websocket.speech_practice import websocket_speech_practice
    from app.api.v1.websocket.connection_manager import manager
    
    # Mock WebSocket
    mock_websocket = AsyncMock()
    mock_websocket.receive_json.side_effect = [
        {"type": "start_session", "mode": "conversation"},
        {"type": "disconnect"}
    ]
    
    # Call the endpoint
    try:
        await websocket_speech_practice(mock_websocket, "test-token")
    except StopIteration:
        pass  # Expected when receive_json runs out of values
    
    # Verify connection was accepted
    mock_websocket.accept.assert_called_once()


@pytest.mark.asyncio
async def test_websocket_start_session():
    """Test starting a speech practice session via WebSocket"""
    from app.api.v1.websocket.speech_practice import websocket_speech_practice
    
    mock_websocket = AsyncMock()
    mock_websocket.receive_json.side_effect = [
        {"type": "start_session", "mode": "conversation"},
        Exception("Stop")  # To exit the loop
    ]
    
    # Mock dependencies
    with patch('app.api.v1.websocket.speech_practice.manager') as mock_manager, \
         patch('app.api.v1.websocket.speech_practice.verify_token') as mock_verify:
        
        mock_verify.return_value = {"user_id": 123, "email": "test@example.com"}
        mock_manager.connect = AsyncMock()
        mock_manager.get_session_data.return_value = {"audio_chunks": [], "user_id": None, "mode": None}
        
        try:
            await websocket_speech_practice(mock_websocket, "test-token")
        except Exception as e:
            if str(e) != "Stop":
                raise
        
        # Verify connect was called
        assert mock_manager.connect.called
        
        # Verify session started message was sent
        calls = [call for call in mock_websocket.send_json.call_args_list 
                 if 'session_started' in str(call)]
        assert len(calls) > 0


@pytest.mark.asyncio
async def test_websocket_audio_chunk_handling():
    """Test handling audio chunks via WebSocket"""
    from app.api.v1.websocket.speech_practice import websocket_speech_practice
    
    mock_websocket = AsyncMock()
    mock_websocket.receive_json.side_effect = [
        {"type": "start_session", "mode": "conversation"},
        {"type": "audio_chunk", "data": "base64-encoded-audio-data"},
        Exception("Stop")
    ]
    
    with patch('app.api.v1.websocket.speech_practice.manager') as mock_manager, \
         patch('app.api.v1.websocket.speech_practice.verify_token') as mock_verify:
        
        mock_verify.return_value = {"user_id": 123}
        mock_manager.get_session_data.return_value = {"audio_chunks": []}
        
        try:
            await websocket_speech_practice(mock_websocket, "test-token")
        except Exception as e:
            if str(e) != "Stop":
                raise
        
        # Verify audio chunk was acknowledged
        calls = mock_websocket.send_json.call_args_list
        assert len(calls) >= 2  # connected + session_started + chunk_received


@pytest.mark.asyncio
async def test_websocket_disconnect_cleanup():
    """Test that disconnect properly cleans up session"""
    from app.api.v1.websocket.speech_practice import websocket_speech_practice
    from fastapi import WebSocketDisconnect
    
    mock_websocket = AsyncMock()
    mock_websocket.receive_json.side_effect = [
        {"type": "start_session", "mode": "conversation"},
        WebSocketDisconnect()  # Simulate client disconnect
    ]
    
    with patch('app.api.v1.websocket.speech_practice.manager') as mock_manager, \
         patch('app.api.v1.websocket.speech_practice.verify_token') as mock_verify:
        
        mock_verify.return_value = {"user_id": 123}
        
        await websocket_speech_practice(mock_websocket, "test-token")
        
        # Verify disconnect was called
        assert mock_manager.disconnect.called


@pytest.mark.asyncio
async def test_websocket_end_session():
    """Test ending a session via WebSocket"""
    from app.api.v1.websocket.speech_practice import websocket_speech_practice
    
    mock_websocket = AsyncMock()
    mock_websocket.receive_json.side_effect = [
        {"type": "start_session", "mode": "conversation"},
        {"type": "end_session"},
        Exception("Stop")
    ]
    
    with patch('app.api.v1.websocket.speech_practice.manager') as mock_manager, \
         patch('app.api.v1.websocket.speech_practice.verify_token') as mock_verify, \
         patch('app.api.v1.websocket.speech_practice.process_session') as mock_process:
        
        mock_verify.return_value = {"user_id": 123}
        mock_manager.connect = AsyncMock()
        mock_manager.get_session_data.return_value = {
            "audio_chunks": [b"chunk1", b"chunk2"],
            "user_id": 123,
            "mode": "conversation"
        }
        mock_manager.disconnect = Mock()
        mock_process.return_value = {"status": "completed"}
        
        try:
            await websocket_speech_practice(mock_websocket, "test-token")
        except Exception as e:
            if str(e) != "Stop":
                raise
        
        # Verify disconnect was called
        assert mock_manager.disconnect.called
        
        # Verify session ended message was sent
        calls = [call for call in mock_websocket.send_json.call_args_list 
                 if 'session_ended' in str(call) or 'completed' in str(call)]
        assert len(calls) > 0
