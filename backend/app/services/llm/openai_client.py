"""OpenAI client implementation for speech analysis."""
from openai import AsyncOpenAI
import json
from typing import Optional, Dict, Any
from app.services.llm.base_client import BaseLLMClient, LLMProviderError


class OpenAIClient(BaseLLMClient):
    """OpenAI client for analyzing speech using GPT models."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", timeout: int = 10000):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4o)
            timeout: Request timeout in milliseconds (default: 10000)
        """
        super().__init__(api_key, timeout)
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.name = "openai"
    
    async def analyze_speech(
        self,
        transcript: str,
        prosody_features: Dict[str, Any],
        reference_text: Optional[str] = None,
        mode: str = "conversation"
    ) -> Dict[str, Any]:
        """
        Analyze speech using OpenAI GPT.
        
        Args:
            transcript: Transcribed speech text
            prosody_features: Extracted prosody features
            reference_text: Optional reference text for comparison
            mode: Practice mode ("conversation", "sentence_practice", "mixed")
        
        Returns:
            Analysis result with scores and feedback
        
        Raises:
            LLMProviderError: If the API call fails
        """
        prompt = self._build_analysis_prompt(
            transcript, prosody_features, reference_text, mode
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
                timeout=self.timeout / 1000  # Convert ms to seconds
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._normalize_response(result)
            
        except Exception as e:
            raise LLMProviderError(f"OpenAI failed: {str(e)}", provider="openai")
    
    async def health_check(self) -> bool:
        """
        Check if OpenAI API is available.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            await self.client.models.list()
            return True
        except:
            return False
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI."""
        return """You are an expert English speech coach specializing in prosody and emotion analysis.
Analyze speech recordings and provide detailed feedback on pronunciation, prosody (intonation, rhythm, stress), 
emotion expression, confidence, and fluency.

Provide scores from 0-10 for each aspect and conversational feedback in Vietnamese.
Be encouraging but honest about areas for improvement."""
    
    def _build_analysis_prompt(
        self,
        transcript: str,
        prosody_features: Dict[str, Any],
        reference_text: Optional[str],
        mode: str
    ) -> str:
        """Build the analysis prompt with speech data."""
        prompt = f"""Analyze this English speech:

Transcript: "{transcript}"
"""
        
        if mode == "sentence_practice" and reference_text:
            prompt += f'Reference text: "{reference_text}"\n'
        
        # Extract prosody metrics
        pitch_mean = prosody_features.get('pitch', {}).get('mean', 0)
        speaking_rate = prosody_features.get('speaking_rate', {}).get('syllables_per_second', 0)
        
        prompt += f"""
Prosody metrics:
- Average pitch: {pitch_mean:.1f} Hz
- Speaking rate: {speaking_rate:.2f} syllables/second

Return a JSON object with this structure:
{{
  "scores": {{
    "overall": 8.5,
    "pronunciation": 9.0,
    "prosody": 7.5,
    "emotion": 8.0,
    "confidence": 7.0,
    "fluency": 9.0
  }},
  "feedback": {{
    "conversational": "Vietnamese feedback for the user...",
    "detailed": {{
      "pronunciation": "Specific pronunciation feedback...",
      "prosody": "Intonation and rhythm feedback...",
      "emotion": "Emotional expression feedback...",
      "suggestions": ["Suggestion 1", "Suggestion 2"]
    }}
  }}
}}
"""
        return prompt
    
    def _normalize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata to the response."""
        return {
            **response,
            "provider": "openai",
            "model": self.model
        }
