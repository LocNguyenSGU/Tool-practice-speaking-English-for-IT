"""Base client interface for LLM providers."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LLMProviderError(Exception):
    """Custom exception for LLM provider errors."""
    
    def __init__(self, message: str, provider: Optional[str] = None):
        super().__init__(message)
        self.provider = provider


class BaseLLMClient(ABC):
    """Abstract base class for LLM provider clients."""
    
    def __init__(self, api_key: str, timeout: int = 30000):
        """
        Initialize the LLM client.
        
        Args:
            api_key: API key for the LLM provider
            timeout: Request timeout in milliseconds (default: 30000)
        """
        self.api_key = api_key
        self.timeout = timeout
    
    @abstractmethod
    async def analyze_speech(
        self,
        transcript: str,
        prosody_features: Dict[str, Any],
        reference_text: Optional[str] = None,
        mode: str = "conversation"
    ) -> Dict[str, Any]:
        """
        Analyze speech and provide feedback.
        
        Args:
            transcript: Transcribed speech text
            prosody_features: Extracted prosody features (pitch, energy, pauses)
            reference_text: Optional reference text for comparison
            mode: Practice mode ("conversation", "reading", "mixed")
        
        Returns:
            Dict containing:
                - scores: Dict with numeric scores (0-10)
                - feedback: Dict with textual feedback
                - prosody_analysis: Optional prosody-specific feedback
        
        Raises:
            LLMProviderError: If the API call fails
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the LLM provider is available.
        
        Returns:
            True if healthy, False otherwise
        """
        pass
