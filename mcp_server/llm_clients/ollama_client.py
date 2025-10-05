"""
Ollama Local LLM Client
Supports local models via Ollama REST API or CLI
"""

import json
import subprocess
import time
from typing import Dict, Optional
import aiohttp
from loguru import logger


class OllamaClient:
    """Client for Ollama local LLM execution"""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 30):
        """
        Initialize Ollama client

        Args:
            base_url: Ollama API base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
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
        Generate response using Ollama

        Args:
            model: Model name (e.g., "llama3", "mistral")
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with provider, model, output, and json fields
        """
        start_time = time.time()

        try:
            # Try REST API first
            result = await self._generate_rest(
                model, prompt, system_prompt, temperature, max_tokens
            )
        except Exception as rest_error:
            logger.warning(f"REST API failed: {rest_error}, trying CLI fallback")
            # Fallback to CLI
            result = await self._generate_cli(model, prompt, system_prompt)

        latency = (time.time() - start_time) * 1000
        result["latency_ms"] = latency

        logger.info(f"Ollama generation completed in {latency:.0f}ms")
        return result

    async def _generate_rest(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Dict:
        """Generate using REST API"""
        url = f"{self.base_url}/api/generate"

        # Build messages
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"

        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error {response.status}: {error_text}")

                data = await response.json()
                output = data.get("response", "")

                return {
                    "provider": "ollama",
                    "model": model,
                    "output": output,
                    "json": self._parse_json(output),
                    "tokens_used": data.get("eval_count")
                }

    async def _generate_cli(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str]
    ) -> Dict:
        """Generate using CLI fallback"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"

        try:
            result = subprocess.run(
                ["ollama", "run", model, full_prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode != 0:
                raise Exception(f"Ollama CLI error: {result.stderr}")

            output = result.stdout.strip()

            return {
                "provider": "ollama",
                "model": model,
                "output": output,
                "json": self._parse_json(output),
                "tokens_used": None
            }

        except subprocess.TimeoutExpired:
            raise Exception(f"Ollama CLI timeout after {self.timeout}s")
        except FileNotFoundError:
            raise Exception("Ollama CLI not found. Please install Ollama.")

    def _parse_json(self, text: str) -> Optional[Dict]:
        """
        Try to extract JSON from response

        Args:
            text: Response text

        Returns:
            Parsed JSON dict or None
        """
        # Try to find JSON in text
        try:
            # Look for JSON object
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Try parsing entire text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    async def list_models(self) -> list:
        """List available Ollama models"""
        url = f"{self.base_url}/api/tags"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")

        return []
