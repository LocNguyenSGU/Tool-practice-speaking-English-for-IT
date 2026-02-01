from fastapi import WebSocket
from typing import Dict, Optional
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for speech practice sessions"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_data: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """
        Accept WebSocket connection and initialize session data
        
        Args:
            websocket: FastAPI WebSocket instance
            session_id: Unique session identifier
        """
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.session_data[session_id] = {
            "audio_chunks": [],
            "start_time": datetime.utcnow()
        }
    
    def disconnect(self, session_id: str):
        """
        Remove WebSocket connection and cleanup session data
        
        Args:
            session_id: Session identifier to disconnect
        """
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.session_data:
            del self.session_data[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        """
        Send JSON message to a specific session
        
        Args:
            session_id: Target session identifier
            message: Dictionary to send as JSON
        """
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)
    
    def get_session_data(self, session_id: str) -> Optional[dict]:
        """
        Get session data for a specific session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data dictionary or None if not found
        """
        return self.session_data.get(session_id)


# Global manager instance
manager = ConnectionManager()
