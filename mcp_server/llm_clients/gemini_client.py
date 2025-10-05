"""
Google Gemini API Client
Supports Gemini 1.5 Pro and Flash models
"""

import time
import json
from typing import Dict, Optional
import google.generativeai as genai
from loguru import logger


class GeminiClient:
    """Client for Google Gemini API"""

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize Gemini client

        Args:
            api_key: Google API key
            timeout: Request timeout in seconds
        """
        genai.configure(api_key=api_key)
        self.timeout = timeout

    async def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """
        Generate response using Gemini

        Args:
            model: Model name (gemini-1.5-pro-latest, gemini-1.5-flash-latest)
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with provider, model, output, and json fields
        """
        start_time = time.time()

        # Build full prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"

        # Configure generation
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        try:
            # Create model
            gemini_model = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config
            )

            # Generate response
            response = gemini_model.generate_content(full_prompt)

            output = response.text

            # Try to get token count
            tokens_used = None
            if hasattr(response, 'usage_metadata'):
                tokens_used = response.usage_metadata.total_token_count

            latency = (time.time() - start_time) * 1000

            logger.info(f"Gemini generation completed in {latency:.0f}ms")

            return {
                "provider": "gemini",
                "model": model,
                "output": output,
                "json": self._parse_json(output),
                "tokens_used": tokens_used,
                "latency_ms": latency
            }

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    def _parse_json(self, text: str) -> Optional[Dict]:
        """
        Try to extract JSON from response

        Args:
            text: Response text

        Returns:
            Parsed JSON dict or None
        """
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object
        try:
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        return None

    async def list_models(self) -> list:
        """List available Gemini models"""
        try:
            models = genai.list_models()
            return [
                model.name.split('/')[-1]
                for model in models
                if 'gemini' in model.name.lower()
            ]
        except Exception as e:
            logger.error(f"Failed to list Gemini models: {e}")
            return []
