from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from app.api.v1.websocket.connection_manager import manager
from app.core.security import verify_token
from typing import Optional
import uuid
import logging
import base64

logger = logging.getLogger(__name__)


async def websocket_speech_practice(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time speech practice
    
    Message types:
    - Client -> Server:
        - {"type": "start_session", "mode": "conversation|sentence_practice"}
        - {"type": "audio_chunk", "data": "base64-encoded-audio"}
        - {"type": "end_session"}
    
    - Server -> Client:
        - {"type": "connected"}
        - {"type": "session_started", "session_id": "..."}
        - {"type": "chunk_received", "chunk_number": 1}
        - {"type": "progress", "message": "..."}
        - {"type": "session_ended", "results": {...}}
        - {"type": "error", "message": "..."}
    """
    session_id: Optional[str] = None
    
    try:
        # Accept connection
        await websocket.accept()
        
        # Verify authentication token
        try:
            user_data = verify_token(token)
            user_id = user_data.get("user_id")
            if not user_id:
                await websocket.send_json({"type": "error", "message": "Invalid token"})
                await websocket.close()
                return
        except Exception as e:
            await websocket.send_json({"type": "error", "message": "Authentication failed"})
            await websocket.close()
            return
        
        # Send connection confirmation
        await websocket.send_json({"type": "connected"})
        
        # Main message loop
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "start_session":
                # Start new session
                session_id = str(uuid.uuid4())
                mode = data.get("mode", "conversation")
                
                await manager.connect(websocket, session_id)
                
                # Store user_id in session data
                session_data = manager.get_session_data(session_id)
                if session_data:
                    session_data["user_id"] = user_id
                    session_data["mode"] = mode
                
                await websocket.send_json({
                    "type": "session_started",
                    "session_id": session_id,
                    "mode": mode
                })
                
                logger.info(f"Session started: {session_id} for user {user_id}")
            
            elif message_type == "audio_chunk":
                # Handle audio chunk
                if not session_id:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No active session. Start a session first."
                    })
                    continue
                
                audio_data = data.get("data")
                if audio_data:
                    # Decode base64 audio data
                    try:
                        audio_bytes = base64.b64decode(audio_data)
                        
                        # Store in session data
                        session_data = manager.get_session_data(session_id)
                        if session_data:
                            session_data["audio_chunks"].append(audio_bytes)
                            chunk_number = len(session_data["audio_chunks"])
                            
                            await websocket.send_json({
                                "type": "chunk_received",
                                "chunk_number": chunk_number
                            })
                    except Exception as e:
                        logger.error(f"Error processing audio chunk: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Failed to process audio chunk"
                        })
            
            elif message_type == "end_session":
                # End session and process audio
                if not session_id:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No active session to end"
                    })
                    continue
                
                await websocket.send_json({
                    "type": "progress",
                    "message": "Processing audio..."
                })
                
                # Get session data
                session_data = manager.get_session_data(session_id)
                
                # Process the session (placeholder - will be implemented with Celery tasks)
                results = await process_session(session_id, session_data)
                
                await websocket.send_json({
                    "type": "session_ended",
                    "results": results
                })
                
                # Cleanup
                manager.disconnect(session_id)
                session_id = None
                
                logger.info(f"Session ended: {session_id}")
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
        if session_id:
            manager.disconnect(session_id)
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if session_id:
            manager.disconnect(session_id)
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass  # Connection may already be closed


async def process_session(session_id: str, session_data: dict) -> dict:
    """
    Process speech practice session
    
    This will trigger Celery tasks for:
    - STT transcription
    - Prosody analysis
    - LLM feedback generation
    
    For now, returns placeholder results
    """
    # Placeholder implementation
    # TODO: Integrate with Celery tasks
    
    audio_chunks = session_data.get("audio_chunks", [])
    mode = session_data.get("mode", "conversation")
    
    return {
        "status": "completed",
        "mode": mode,
        "chunks_processed": len(audio_chunks),
        "message": "Session processing complete (placeholder)"
    }
