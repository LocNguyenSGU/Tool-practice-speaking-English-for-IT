"""LLM orchestrator with multi-provider fallback and circuit breaker."""
from sqlalchemy.orm import Session
from app.services.llm.openai_client import OpenAIClient
from app.services.llm.gemini_client import GeminiClient
from app.services.llm_key_rotation import LLMKeyRotationService
from app.services.llm.base_client import LLMProviderError
from typing import Optional, Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)


class LLMOrchestrator:
    """
    Orchestrates LLM providers with priority-based fallback.
    
    Priority chain: OpenAI (gpt-4o) → Gemini (2.0-flash) → Degraded mode
    """
    
    def __init__(self, db: Session, encryption_key: str):
        """
        Initialize orchestrator.
        
        Args:
            db: Database session
            encryption_key: Encryption key for API keys
        """
        self.db = db
        self.key_service = LLMKeyRotationService(db, encryption_key)
        self.priority_chain = ["openai", "gemini"]  # Ordered by priority
    
    async def analyze_speech(
        self,
        transcript: str,
        prosody_features: Dict[str, Any],
        reference_text: Optional[str] = None,
        mode: str = "conversation",
        session_id: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze speech using available LLM providers with automatic fallback.
        
        Args:
            transcript: Transcribed speech text
            prosody_features: Extracted prosody features
            reference_text: Optional reference text for comparison
            mode: Practice mode ("conversation", "sentence_practice", "mixed")
            session_id: Session ID for tracking
            user_id: User ID for tracking
        
        Returns:
            Analysis result with scores, feedback, and provider metadata
        """
        for provider_name in self.priority_chain:
            try:
                result = await self._try_provider(
                    provider_name,
                    transcript,
                    prosody_features,
                    reference_text,
                    mode
                )
                
                if result:
                    return {
                        **result,
                        "provider_used": provider_name,
                        "was_degraded": False
                    }
                    
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {str(e)}")
                continue
        
        # All providers failed - return degraded response
        logger.error("All LLM providers failed, using degraded mode")
        return self._get_degraded_response(transcript, prosody_features)
    
    async def _try_provider(
        self,
        provider_name: str,
        transcript: str,
        prosody_features: Dict[str, Any],
        reference_text: Optional[str],
        mode: str
    ) -> Optional[Dict[str, Any]]:
        """
        Try to analyze speech using a specific provider.
        
        Returns:
            Analysis result or None if provider unavailable/failed
        """
        # Get API key from rotation service
        api_key_record = self.key_service.get_available_key(provider_name)
        
        if not api_key_record:
            logger.warning(f"No available API key for {provider_name}")
            return None
        
        # Decrypt API key
        api_key = self.key_service.decrypt_api_key(api_key_record.api_key_encrypted)
        
        # Create provider client
        client = self._create_client(provider_name, api_key)
        
        try:
            # Call with timeout
            result = await asyncio.wait_for(
                client.analyze_speech(
                    transcript,
                    prosody_features,
                    reference_text,
                    mode
                ),
                timeout=client.timeout / 1000  # Convert ms to seconds
            )
            
            # Record success
            self.key_service.record_success(
                api_key_id=api_key_record.id,
                tokens_used=100,  # Placeholder - would extract from response
                latency_seconds=1.0  # Placeholder - would measure actual time
            )
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Provider {provider_name} timeout")
            self.key_service.record_failure(api_key_record.id, "Timeout")
            raise
            
        except LLMProviderError as e:
            logger.error(f"Provider {provider_name} error: {str(e)}")
            self.key_service.record_failure(api_key_record.id, str(e))
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error with {provider_name}: {str(e)}")
            self.key_service.record_failure(api_key_record.id, str(e))
            raise
    
    def _create_client(self, provider_name: str, api_key: str):
        """
        Create LLM client instance.
        
        Args:
            provider_name: Name of the provider
            api_key: Decrypted API key
        
        Returns:
            LLM client instance
        """
        if provider_name == "openai":
            return OpenAIClient(api_key)
        elif provider_name == "gemini":
            return GeminiClient(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    def _get_degraded_response(
        self,
        transcript: str,
        prosody_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate basic response when all LLM providers fail.
        
        Uses simple heuristics based on prosody features.
        
        Args:
            transcript: Transcribed text
            prosody_features: Prosody analysis
        
        Returns:
            Degraded analysis with basic scores
        """
        # Simple scoring based on prosody
        pitch_mean = prosody_features.get('pitch', {}).get('mean', 180)
        speaking_rate = prosody_features.get('speaking_rate', {}).get('syllables_per_second', 3.0)
        
        # Basic heuristics
        pitch_score = min(10, max(5, (pitch_mean - 100) / 20))
        rate_score = min(10, max(5, speaking_rate * 2))
        
        overall_score = (pitch_score + rate_score) / 2
        
        return {
            "scores": {
                "overall": round(overall_score, 1),
                "pronunciation": 7.0,
                "prosody": round(pitch_score, 1),
                "emotion": 7.0,
                "confidence": 7.0,
                "fluency": round(rate_score, 1)
            },
            "feedback": {
                "conversational": "Hệ thống đang bận, vui lòng thử lại sau. Chúng tôi đã ghi nhận bài tập của bạn.",
                "detailed": {
                    "pronunciation": "Không thể phân tích chi tiết lúc này",
                    "suggestions": ["Vui lòng thử lại sau"]
                }
            },
            "provider_used": "degraded",
            "was_degraded": True
        }
