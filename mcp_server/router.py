"""
MCP Router - Routes requests to appropriate LLM providers
"""

import asyncio
from typing import Dict, Optional, Tuple
from loguru import logger

from .schema import MCPCommand, LLMResponse, LLMResponseMetadata, LLMError, MCPResponse
from .llm_clients import OllamaClient, OpenAIClient, GeminiClient, ClaudeClient
from .utils import Config
from datetime import datetime


class MCPRouter:
    """Routes MCP commands to appropriate LLM clients"""

    def __init__(self, config: Config):
        """
        Initialize router with configuration

        Args:
            config: Configuration object
        """
        self.config = config
        self.clients = {}

        # Initialize clients based on available API keys
        if config.ollama_url:
            self.clients["ollama"] = OllamaClient(
                base_url=config.ollama_url,
                timeout=config.timeout_seconds
            )

        if config.openai_api_key:
            self.clients["openai"] = OpenAIClient(
                api_key=config.openai_api_key,
                timeout=config.timeout_seconds
            )

        if config.gemini_api_key:
            self.clients["gemini"] = GeminiClient(
                api_key=config.gemini_api_key,
                timeout=config.timeout_seconds
            )

        if config.claude_api_key:
            self.clients["claude"] = ClaudeClient(
                api_key=config.claude_api_key,
                timeout=config.timeout_seconds
            )

        logger.info(f"Initialized MCP Router with providers: {list(self.clients.keys())}")

    async def route_command(
        self,
        command: MCPCommand,
        system_prompt: Optional[str] = None
    ) -> MCPResponse:
        """
        Route command to appropriate LLM

        Args:
            command: MCP command to process
            system_prompt: System prompt to use

        Returns:
            MCP response with actions or errors
        """
        if command.command == "ask_model":
            return await self._handle_ask_model(command, system_prompt)
        elif command.command == "list_models":
            return await self._handle_list_models()
        elif command.command == "health_check":
            return await self._handle_health_check()
        else:
            return MCPResponse(
                status="error",
                message=f"Unknown command: {command.command}",
                actions_to_execute=[]
            )

    async def _handle_ask_model(
        self,
        command: MCPCommand,
        system_prompt: Optional[str]
    ) -> MCPResponse:
        """Handle ask_model command"""
        if not command.params:
            return MCPResponse(
                status="error",
                message="Missing model parameters",
                actions_to_execute=[]
            )

        provider = command.params.provider
        model = command.params.model
        prompt = command.params.prompt

        # Build context-aware prompt
        if command.context:
            context_str = f"\nDesign Context:\n"
            context_str += f"- Active Component: {command.context.active_component}\n"
            context_str += f"- Units: {command.context.units}\n"
            context_str += f"- Design State: {command.context.design_state}\n"
            prompt = context_str + "\n" + prompt

        # Try primary provider
        llm_response = await self._generate_with_retry(
            provider=provider,
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=command.params.temperature,
            max_tokens=command.params.max_tokens
        )

        # If failed and fallback chain exists, try fallback
        if not llm_response.success and self.config.fallback_chain:
            logger.warning(f"Primary provider {provider} failed, trying fallback chain")
            for fallback in self.config.fallback_chain:
                fallback_provider, fallback_model = self._parse_model_string(fallback)
                llm_response = await self._generate_with_retry(
                    provider=fallback_provider,
                    model=fallback_model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=command.params.temperature,
                    max_tokens=command.params.max_tokens
                )
                if llm_response.success:
                    break

        # Build MCP response
        if llm_response.success:
            actions = []
            if llm_response.action:
                actions.append(llm_response.action)
            elif llm_response.action_sequence:
                actions.extend(llm_response.action_sequence.actions)

            status = "success" if actions else "clarification_needed"
            message = "Action generated successfully" if actions else "Need clarification"

            return MCPResponse(
                status=status,
                llm_response=llm_response,
                message=message,
                actions_to_execute=actions
            )
        else:
            return MCPResponse(
                status="error",
                llm_response=llm_response,
                message=f"All providers failed: {llm_response.error.message if llm_response.error else 'Unknown error'}",
                actions_to_execute=[]
            )

    async def _generate_with_retry(
        self,
        provider: str,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """
        Generate with retry logic

        Args:
            provider: Provider name
            model: Model name
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature
            max_tokens: Max tokens

        Returns:
            LLM response
        """
        if provider not in self.clients:
            return LLMResponse(
                success=False,
                provider=provider,
                model=model,
                raw_output="",
                metadata=LLMResponseMetadata(provider=provider, model=model),
                error=LLMError(
                    type="provider_not_available",
                    message=f"Provider {provider} not configured",
                    provider=provider,
                    recoverable=False
                )
            )

        client = self.clients[provider]
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                result = await client.generate(
                    model=model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                # Parse action from JSON response
                action = None
                action_sequence = None
                if result.get("json"):
                    from .schema import FusionAction, ActionSequence
                    try:
                        if "actions" in result["json"]:
                            action_sequence = ActionSequence(**result["json"])
                        elif "action" in result["json"]:
                            action = FusionAction(**result["json"])
                    except Exception as e:
                        logger.warning(f"Failed to parse action from JSON: {e}")

                return LLMResponse(
                    success=True,
                    provider=result["provider"],
                    model=result["model"],
                    raw_output=result["output"],
                    action=action,
                    action_sequence=action_sequence,
                    metadata=LLMResponseMetadata(
                        provider=result["provider"],
                        model=result["model"],
                        tokens_used=result.get("tokens_used"),
                        latency_ms=result.get("latency_ms"),
                        temperature=temperature
                    )
                )

            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed for {provider}: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay)

        # All retries failed
        return LLMResponse(
            success=False,
            provider=provider,
            model=model,
            raw_output="",
            metadata=LLMResponseMetadata(provider=provider, model=model),
            error=LLMError(
                type="generation_failed",
                message=str(last_error),
                provider=provider,
                retry_count=self.config.max_retries,
                recoverable=True
            )
        )

    async def _handle_list_models(self) -> MCPResponse:
        """List available models from all providers"""
        models = {}
        for provider, client in self.clients.items():
            try:
                provider_models = await client.list_models()
                models[provider] = provider_models
            except Exception as e:
                logger.error(f"Failed to list models for {provider}: {e}")
                models[provider] = []

        return MCPResponse(
            status="success",
            message="Models listed successfully",
            actions_to_execute=[],
            llm_response=LLMResponse(
                success=True,
                provider="system",
                model="list_models",
                raw_output=str(models),
                metadata=LLMResponseMetadata(provider="system", model="list_models")
            )
        )

    async def _handle_health_check(self) -> MCPResponse:
        """Check health of all providers"""
        health = {}
        for provider in self.clients.keys():
            health[provider] = "available"

        return MCPResponse(
            status="success",
            message=f"Healthy providers: {list(health.keys())}",
            actions_to_execute=[]
        )

    def _parse_model_string(self, model_string: str) -> Tuple[str, str]:
        """
        Parse model string like 'openai:gpt-4o-mini'

        Args:
            model_string: Model string in format 'provider:model'

        Returns:
            Tuple of (provider, model)
        """
        if ':' in model_string:
            parts = model_string.split(':', 1)
            return parts[0], parts[1]
        else:
            # Assume it's just a model, use default provider
            return "openai", model_string
