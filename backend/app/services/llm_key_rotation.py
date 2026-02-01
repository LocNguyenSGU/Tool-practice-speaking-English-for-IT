from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.llm_provider import LLMProviderConfig, LLMAPIKey
from app.services.encryption_service import EncryptionService
from datetime import datetime
from typing import Optional

class LLMKeyRotationService:
    """Service for managing LLM API key rotation and encryption"""
    
    def __init__(self, db: Session, encryption_key: str):
        """
        Initialize the key rotation service
        
        Args:
            db: Database session
            encryption_key: Key for encrypting/decrypting API keys
        """
        self.db = db
        self.encryption_service = EncryptionService(encryption_key)
    
    def get_available_key(self, provider_name: str) -> Optional[LLMAPIKey]:
        """
        Get an available API key for the given provider using LRU rotation
        
        Args:
            provider_name: Name of the LLM provider (openai, gemini, etc.)
            
        Returns:
            LLMAPIKey instance or None if no active keys available
        """
        # Get active keys for this provider, ordered by least recently used
        keys = self.db.query(LLMAPIKey).join(LLMProviderConfig).filter(
            and_(
                LLMProviderConfig.provider_name == provider_name,
                LLMProviderConfig.is_active == True,
                LLMAPIKey.is_active == True
            )
        ).order_by(
            LLMAPIKey.last_used_at.asc().nullsfirst()  # NULL values first (never used)
        ).all()
        
        if not keys:
            return None
        
        # Return least recently used key
        return keys[0]
    
    def encrypt_api_key(self, api_key: str) -> str:
        """
        Encrypt an API key for storage
        
        Args:
            api_key: Plain text API key
            
        Returns:
            Encrypted API key
        """
        return self.encryption_service.encrypt_api_key(api_key)
    
    def decrypt_api_key(self, encrypted_api_key: str) -> str:
        """
        Decrypt an API key from storage
        
        Args:
            encrypted_api_key: Encrypted API key
            
        Returns:
            Plain text API key
        """
        return self.encryption_service.decrypt_api_key(encrypted_api_key)
    
    def record_success(self, api_key_id: int, tokens_used: int = 0, latency_seconds: float = 0):
        """
        Record a successful API call
        
        Args:
            api_key_id: ID of the API key used
            tokens_used: Number of tokens consumed
            latency_seconds: Request latency in seconds
        """
        key = self.db.query(LLMAPIKey).filter(LLMAPIKey.id == api_key_id).first()
        if key:
            key.request_count += 1
            key.last_used_at = datetime.utcnow()
            self.db.commit()
    
    def record_failure(self, api_key_id: int, error_message: str):
        """
        Record a failed API call
        
        Args:
            api_key_id: ID of the API key used
            error_message: Error message from the failure
        """
        key = self.db.query(LLMAPIKey).filter(LLMAPIKey.id == api_key_id).first()
        if key:
            key.failure_count += 1
            key.last_failure_at = datetime.utcnow()
            self.db.commit()
