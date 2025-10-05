"""
Anthropic Claude API Client
Supports Claude 3.5 Sonnet and other models
"""

import time
from typing import Dict, Optional
from anthropic import AsyncAnthropic
from loguru import logger


class ClaudeClient:
    """Client for Anthropic Claude API"""

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key
            timeout: Request timeout in seconds
        """
        self.client = AsyncAnthropic(api_key=api_key, timeout=timeout)
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
        Generate response using Claude

        Args:
            model: Model name (claude-3-5-sonnet-20241022, etc.)
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with provider, model, output, and json fields
        """
        start_time = time.time()

        # Build messages
        messages = [{"role": "user", "content": prompt}]

        # Prepare request params
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # Add system prompt if provided
        if system_prompt:
            params["system"] = system_prompt

        try:
            response = await self.client.messages.create(**params)

            output = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            latency = (time.time() - start_time) * 1000

            logger.info(f"Claude generation completed in {latency:.0f}ms, {tokens_used} tokens")

            return {
                "provider": "claude",
                "model": model,
                "output": output,
                "json": self._parse_json(output),
                "tokens_used": tokens_used,
                "latency_ms": latency
            }

        except Exception as e:
            logger.error(f"Claude API error: {e}")
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
