"""
MCP FastAPI Server
Main entry point for the Fusion 360 MCP integration
"""

import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from .schema import MCPCommand, MCPResponse
from .router import MCPRouter
from .utils import load_config, setup_logger, ContextCache


# Global instances
config = None
router = None
cache = None
system_prompt = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global config, router, cache, system_prompt

    # Startup
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded")

        # Setup logging
        setup_logger(
            log_level=config.log_level,
            log_dir=config.log_dir
        )

        # Initialize cache
        if config.cache_enabled:
            cache = ContextCache(
                cache_type=config.cache_type,
                cache_path=config.cache_path
            )
            logger.info(f"Cache initialized: {config.cache_type}")

        # Load system prompt
        system_prompt_path = Path("prompts/system_prompt.md")
        if system_prompt_path.exists():
            system_prompt = system_prompt_path.read_text()
            logger.info("System prompt loaded")
        else:
            logger.warning("System prompt not found, using default")
            system_prompt = "You are FusionMCP, a parametric CAD design assistant."

        # Initialize router
        router = MCPRouter(config)

        logger.info(f"MCP Server started on {config.mcp_host}:{config.mcp_port}")

    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

    yield

    # Shutdown
    if cache:
        cache.close()
    logger.info("MCP Server shut down")


# Create FastAPI app
app = FastAPI(
    title="Fusion 360 MCP Server",
    description="Multi-model MCP integration for Autodesk Fusion 360",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if config and config.allow_remote else ["http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/mcp/command", response_model=MCPResponse)
async def execute_command(command: MCPCommand) -> MCPResponse:
    """
    Execute MCP command

    Args:
        command: MCP command to execute

    Returns:
        MCP response with actions or errors
    """
    try:
        logger.info(f"Received command: {command.command}")

        # Route command
        response = await router.route_command(command, system_prompt)

        # Cache conversation if enabled
        if cache and command.command == "ask_model" and response.llm_response:
            cache.save_conversation(
                user_input=command.params.prompt if command.params else "",
                llm_response=response.llm_response.raw_output,
                provider=response.llm_response.provider,
                model=response.llm_response.model
            )

        # Cache design context if provided
        if cache and command.context:
            cache.save_design_state(command.context.model_dump())

        return response

    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/execute_action")
async def execute_action(action_data: dict) -> dict:
    """
    Log action execution result

    Args:
        action_data: Action execution data

    Returns:
        Acknowledgment
    """
    try:
        if cache:
            cache.save_action(
                action_type=action_data.get("action", "unknown"),
                action_data=action_data.get("params", {}),
                success=action_data.get("success", False),
                error_message=action_data.get("error")
            )

        return {"status": "logged"}

    except Exception as e:
        logger.error(f"Failed to log action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "providers": list(router.clients.keys()) if router else [],
        "cache_enabled": config.cache_enabled if config else False
    }


@app.get("/models")
async def list_models() -> dict:
    """List available models"""
    if not router:
        raise HTTPException(status_code=503, detail="Router not initialized")

    response = await router._handle_list_models()
    return {"models": response.llm_response.raw_output if response.llm_response else {}}


@app.get("/history")
async def get_history(limit: int = 10) -> dict:
    """Get conversation history"""
    if not cache:
        raise HTTPException(status_code=503, detail="Cache not enabled")

    conversations = cache.get_recent_conversations(limit)
    actions = cache.get_recent_actions(limit * 2)

    return {
        "conversations": conversations,
        "actions": actions
    }


def main():
    """Main entry point"""
    import uvicorn

    # Load config for port
    cfg = load_config()

    uvicorn.run(
        "mcp_server.server:app",
        host=cfg.mcp_host,
        port=cfg.mcp_port,
        reload=False,
        log_level=cfg.log_level.lower()
    )


if __name__ == "__main__":
    main()
