"""Gemini client implementation for speech analysis."""
import google.generativeai as genai
import json
from typing import Optional, Dict, Any
from app.services.llm.base_client import BaseLLMClient, LLMProviderError


class GeminiClient(BaseLLMClient):
    """Gemini client for analyzing speech using Google's Gemini models."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp", timeout: int = 10000):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google API key
            model: Model name (default: gemini-2.0-flash-exp)
            timeout: Request timeout in milliseconds (default: 10000)
        """
        super().__init__(api_key, timeout)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": 0.7,
                "response_mime_type": "application/json"
            }
        )
        self.model_name = model
        self.name = "gemini"
    
    async def analyze_speech(
        self,
        transcript: str,
        prosody_features: Dict[str, Any],
        reference_text: Optional[str] = None,
        mode: str = "conversation"
    ) -> Dict[str, Any]:
        """
        Analyze speech using Gemini.
        
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
            response = await self.model.generate_content_async(
                prompt,
                request_options={"timeout": self.timeout / 1000}  # Convert ms to seconds
            )
            
            result = json.loads(response.text)
            return self._normalize_response(result)
            
        except Exception as e:
            raise LLMProviderError(f"Gemini failed: {str(e)}", provider="gemini")
    
    async def health_check(self) -> bool:
        """
        Check if Gemini API is available.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            await self.model.generate_content_async("ping")
            return True
        except:
            return False
    
    def _build_analysis_prompt(
        self,
        transcript: str,
        prosody_features: Dict[str, Any],
        reference_text: Optional[str],
        mode: str
    ) -> str:
        """Build the analysis prompt with speech data."""
        prompt = f"""You are an expert English speech coach. Analyze this speech recording:

Transcript: "{transcript}"
"""
        
        if mode == "sentence_practice" and reference_text:
            prompt += f'Reference text: "{reference_text}"\n'
        
        # Extract prosody metrics
        pitch_mean = prosody_features.get('pitch', {}).get('mean', 0)
        speaking_rate = prosody_features.get('speaking_rate', {}).get('syllables_per_second', 0)
        
        prompt += f"""
Prosody analysis:
- Average pitch: {pitch_mean:.1f} Hz
- Speaking rate: {speaking_rate:.2f} syllables/second

Provide detailed analysis with scores (0-10) for:
1. Overall quality
2. Pronunciation accuracy
3. Prosody (intonation, rhythm, stress)
4. Emotional expression
5. Confidence in delivery
6. Fluency

Return your analysis as JSON:
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
    "conversational": "Feedback in Vietnamese for the user...",
    "detailed": {{
      "pronunciation": "Detailed feedback on pronunciation...",
      "prosody": "Feedback on intonation and rhythm...",
      "emotion": "Feedback on emotional expression...",
      "suggestions": ["Improvement suggestion 1", "Suggestion 2"]
    }}
  }}
}}
"""
        return prompt
    
    def _normalize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata to the response."""
        return {
            **response,
            "provider": "gemini",
            "model": self.model_name
        }
