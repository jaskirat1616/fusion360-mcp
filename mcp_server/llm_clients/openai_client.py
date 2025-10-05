"""
OpenAI API Client
Supports GPT-4, GPT-4o, and GPT-4o-mini
"""

import time
from typing import Dict, Optional
from openai import AsyncOpenAI
from loguru import logger


class OpenAIClient:
    """Client for OpenAI API"""

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize OpenAI client

        Args:
            api_key: OpenAI API key
            timeout: Request timeout in seconds
        """
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout)
        self.timeout = timeout

    async def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        json_mode: bool = True
    ) -> Dict:
        """
        Generate response using OpenAI

        Args:
            model: Model name (gpt-4o, gpt-4o-mini, etc.)
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            json_mode: Whether to force JSON output

        Returns:
            Dict with provider, model, output, and json fields
        """
        start_time = time.time()

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Prepare request params
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # Enable JSON mode for supported models
        if json_mode and ("gpt-4" in model or "gpt-3.5" in model):
            params["response_format"] = {"type": "json_object"}
            # Add JSON instruction to system prompt
            if system_prompt:
                messages[0]["content"] += "\n\nYou must respond with valid JSON."
            else:
                messages.insert(0, {
                    "role": "system",
                    "content": "You must respond with valid JSON."
                })

        try:
            response = await self.client.chat.completions.create(**params)

            output = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            latency = (time.time() - start_time) * 1000

            logger.info(f"OpenAI generation completed in {latency:.0f}ms, {tokens_used} tokens")

            return {
                "provider": "openai",
                "model": model,
                "output": output,
                "json": self._parse_json(output),
                "tokens_used": tokens_used,
                "latency_ms": latency
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _parse_json(self, text: str) -> Optional[Dict]:
        """
        Try to extract JSON from response

        Args:
            text: Response text

        Returns:
            Parsed JSON dict or None
        """
        import json

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
        """List available OpenAI models"""
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data if "gpt" in model.id]
        except Exception as e:
            logger.error(f"Failed to list OpenAI models: {e}")
            return []
