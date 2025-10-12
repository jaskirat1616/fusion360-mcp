# FusionMCP Architecture Documentation

## System Overview

FusionMCP implements a **Model Context Protocol (MCP)** architecture that acts as a unified interface between Autodesk Fusion 360 and multiple Large Language Model (LLM) providers.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER LAYER                                 │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐      │
│  │             Autodesk Fusion 360                        │      │
│  │  - User inputs natural language                        │      │
│  │  - Receives structured JSON actions                    │      │
│  │  - Executes CAD operations                             │      │
│  └─────────────────────┬──────────────────────────────────┘      │
│                        │                                          │
└────────────────────────┼──────────────────────────────────────────┘
                         │ HTTP/REST (JSON)
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│                     INTEGRATION LAYER                             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐      │
│  │           Fusion 360 Python Add-in                     │      │
│  │                                                         │      │
│  │  Components:                                           │      │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │      │
│  │  │  UI Dialog  │  │   Network    │  │   Action     │  │      │
│  │  │             │→ │   Client     │→ │  Executor    │  │      │
│  │  │  - Input    │  │              │  │              │  │      │
│  │  │  - Display  │  │  - HTTP      │  │  - Geometry  │  │      │
│  │  └─────────────┘  │  - JSON      │  │  - Features  │  │      │
│  │                   └──────────────┘  └──────────────┘  │      │
│  │                                                         │      │
│  │  Responsibilities:                                     │      │
│  │  • Capture user intent                                │      │
│  │  • Serialize design context                           │      │
│  │  • Send commands to MCP server                        │      │
│  │  • Execute returned actions in Fusion API             │      │
│  │  • Provide real-time feedback                         │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                   │
└────────────────────────┼──────────────────────────────────────────┘
                         │ POST /mcp/command
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│                      MCP SERVER LAYER                             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐      │
│  │              FastAPI MCP Server                        │      │
│  │                                                         │      │
│  │  ┌──────────────────────────────────────────────┐     │      │
│  │  │            Router (router.py)                │     │      │
│  │  │                                               │     │      │
│  │  │  • Parse MCP commands                        │     │      │
│  │  │  • Route to appropriate LLM client           │     │      │
│  │  │  • Handle fallback chain                     │     │      │
│  │  │  • Retry logic (max 3 attempts)              │     │      │
│  │  │  • Response normalization                    │     │      │
│  │  └──────────────────────────────────────────────┘     │      │
│  │                                                         │      │
│  │  ┌──────────────────────────────────────────────┐     │      │
│  │  │          Schema Validation                   │     │      │
│  │  │                                               │     │      │
│  │  │  • MCPCommand (Pydantic)                     │     │      │
│  │  │  • FusionAction (Pydantic)                   │     │      │
│  │  │  • LLMResponse (Pydantic)                    │     │      │
│  │  │  • Type safety and validation                │     │      │
│  │  └──────────────────────────────────────────────┘     │      │
│  │                                                         │      │
│  │  ┌──────────────────────────────────────────────┐     │      │
│  │  │          Context Cache                       │     │      │
│  │  │                                               │     │      │
│  │  │  • Conversation history                      │     │      │
│  │  │  • Design state snapshots                    │     │      │
│  │  │  • Action execution logs                     │     │      │
│  │  │  • Backend: JSON or SQLite                   │     │      │
│  │  └──────────────────────────────────────────────┘     │      │
│  │                                                         │      │
│  │  Endpoints:                                            │      │
│  │  • POST /mcp/command    - Execute MCP command         │      │
│  │  • POST /mcp/execute    - Log action execution        │      │
│  │  • GET  /health         - Health check                │      │
│  │  • GET  /models         - List available models       │      │
│  │  • GET  /history        - Conversation history        │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                   │
└──────────┬─────────────┬─────────────┬─────────────┬─────────────┘
           │             │             │             │
           ↓             ↓             ↓             ↓
┌──────────────────────────────────────────────────────────────────┐
│                       LLM CLIENT LAYER                            │
│                                                                   │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│  │ Ollama   │    │ OpenAI   │    │ Gemini   │    │ Claude   │   │
│  │ Client   │    │ Client   │    │ Client   │    │ Client   │   │
│  │          │    │          │    │          │    │          │   │
│  │ • Local  │    │ • GPT-4o │    │ • Gemini │    │ • Claude │   │
│  │ • Llama3 │    │ • 4o-mini│    │   1.5 Pro│    │   3.5    │   │
│  │ • Mistral│    │ • Turbo  │    │ • Flash  │    │ • Opus   │   │
│  │          │    │          │    │          │    │          │   │
│  │ Offline  │    │ REST API │    │ REST API │    │ REST API │   │
│  │ Free     │    │ $$       │    │ $        │    │ $$$      │   │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘   │
│       │               │               │               │          │
│       └───────────────┴───────────────┴───────────────┘          │
│                           │                                       │
│              Unified Interface: generate(model, prompt, ...)     │
│                           │                                       │
│              Returns: {provider, model, output, json, tokens}    │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│                    INTELLIGENCE LAYER                             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐      │
│  │              System Prompt (FusionMCP)                 │      │
│  │                                                         │      │
│  │  Core Principles:                                      │      │
│  │  • Structured JSON output only                        │      │
│  │  • Parametric design reasoning                        │      │
│  │  • Safety validation (dimensions, units, feasibility) │      │
│  │  • Clarifying questions for ambiguous requests        │      │
│  │                                                         │      │
│  │  Action Schema:                                        │      │
│  │  {                                                     │      │
│  │    "action": "verb_noun",                             │      │
│  │    "params": {...},                                   │      │
│  │    "explanation": "...",                              │      │
│  │    "safety_checks": [...],                            │      │
│  │    "dependencies": [...]                              │      │
│  │  }                                                     │      │
│  │                                                         │      │
│  │  Multi-Model Orchestration:                           │      │
│  │  • Gemini   → Geometric reasoning                     │      │
│  │  • OpenAI   → Creative synthesis                      │      │
│  │  • Claude   → Safety validation, structure            │      │
│  │  • Ollama   → Offline fallback                        │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Request Flow

```
User → Fusion UI → Add-in → MCP Server → LLM Client → LLM API
                                                           ↓
User ← Fusion API ← Add-in ← MCP Server ← LLM Client ← Response
```

**Steps**:
1. User enters natural language in Fusion 360
2. Add-in captures input and design context
3. Add-in sends `MCPCommand` to server via HTTP POST
4. Server validates command using Pydantic schemas
5. Router selects appropriate LLM client
6. Client formats prompt with system prompt
7. LLM generates structured JSON response
8. Server parses and validates `FusionAction`
9. Server returns `MCPResponse` to add-in
10. Add-in executes actions using Fusion 360 API

### 2. Fallback Chain Flow

```
Primary Model (OpenAI)
         ↓ [Fails]
Fallback 1 (Gemini)
         ↓ [Fails]
Fallback 2 (Ollama)
         ↓ [Success]
Return Response
```

**Configuration**:
```json
{
  "default_model": "openai:gpt-4o-mini",
  "fallback_chain": [
    "openai:gpt-4o-mini",
    "gemini:gemini-1.5-flash-latest",
    "ollama:llama3"
  ]
}
```

### 3. Retry Logic

```
Attempt 1 → [Timeout/Error] → Wait 1s
Attempt 2 → [Timeout/Error] → Wait 1s
Attempt 3 → [Timeout/Error] → Return Error
```

**Configuration**:
- `max_retries`: 3
- `retry_delay`: 1.0s
- `timeout_seconds`: 30s

## Key Components

### 1. Fusion 360 Add-in (`fusion_addin/`)

**main.py** - Entry point
- Registers add-in with Fusion 360
- Creates UI command button
- Handles lifecycle (start/stop)

**ui_dialog.py** - User interface
- Displays MCP Assistant palette
- Captures user input
- Shows real-time feedback
- Manages model selection

**fusion_actions.py** - Action executor
- `execute()` - Routes actions to appropriate handlers
- `_create_box()` - Creates boxes using extrude
- `_create_cylinder()` - Creates cylinders
- `_create_sphere()` - Creates spheres using revolve
- `_create_hole()` - Creates holes (cut operation)
- Unit conversion utilities

**utils/network.py** - Network client
- `send_command()` - Sends HTTP POST to MCP server
- `check_health()` - Health check
- `list_models()` - Query available models
- Error handling and timeouts

### 2. MCP Server (`mcp_server/`)

**server.py** - FastAPI application
- Endpoint definitions
- Request/response handling
- Lifespan management (startup/shutdown)
- CORS middleware

**router.py** - Request router
- `route_command()` - Main routing logic
- `_handle_ask_model()` - Processes AI requests
- `_generate_with_retry()` - Retry logic
- Fallback chain implementation
- Response normalization

**schema/** - Pydantic models
- `mcp_command.py` - Input command schemas
- `fusion_action.py` - CAD action schemas
- `llm_response.py` - LLM response schemas
- Type validation and serialization

**llm_clients/** - LLM implementations
- `ollama_client.py` - Local Ollama REST/CLI
- `openai_client.py` - OpenAI API with JSON mode
- `gemini_client.py` - Google Gemini API
- `claude_client.py` - Anthropic Claude API
- Unified `generate()` interface

**utils/** - Utilities
- `logger.py` - Loguru setup (console + file)
- `config_loader.py` - Config from JSON/env vars
- `context_cache.py` - Conversation/state persistence

### 3. System Prompt (`prompts/system_prompt.md`)

**Purpose**: Defines FusionMCP's behavior and capabilities

**Key Sections**:
1. **Core Principles** - JSON-only output, parametric reasoning, safety
2. **Supported Actions** - Complete action catalog with params
3. **Design Context Awareness** - How to use context data
4. **Clarification Protocol** - When/how to ask questions
5. **Safety Checks** - Validation requirements
6. **Example Interactions** - Response templates

## Communication Protocols

### HTTP REST API

**Request Format**:
```json
POST /mcp/command
{
  "command": "ask_model",
  "params": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "prompt": "Create a 20mm cube",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "context": {
    "active_component": "RootComponent",
    "units": "mm",
    "design_state": "empty",
    "geometry_count": {"bodies": 0}
  }
}
```

**Response Format**:
```json
{
  "status": "success|error|clarification_needed",
  "message": "Human-readable message",
  "actions_to_execute": [
    {
      "action": "create_box",
      "params": {"width": 20, "height": 20, "depth": 20, "unit": "mm"},
      "explanation": "Creating 20mm cube",
      "safety_checks": ["dimensions_positive", "units_valid"]
    }
  ],
  "llm_response": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "raw_output": "...",
    "metadata": {...}
  }
}
```

### Action Schema

**Base Structure**:
```typescript
interface FusionAction {
  action: string;              // "create_box", "create_cylinder", etc.
  params: object;              // Action-specific parameters
  explanation?: string;        // Human-readable summary
  safety_checks?: string[];    // Validations performed
  dependencies?: string[];     // Required prior actions
}
```

**Supported Actions**:
- `create_box` - Rectangular box
- `create_cylinder` - Cylinder
- `create_sphere` - Sphere (via revolve)
- `create_hole` - Cylindrical hole (cut)
- `extrude` - Extrude profile
- `fillet` - Round edges
- `apply_material` - Set material

## Error Handling

### Error Types

1. **Network Errors** - Connection failures, timeouts
2. **API Errors** - Invalid keys, rate limits, model errors
3. **Validation Errors** - Invalid JSON, missing fields
4. **Execution Errors** - Fusion API failures

### Error Response Format

```json
{
  "status": "error",
  "message": "Detailed error message",
  "llm_response": {
    "error": {
      "type": "timeout|api_error|validation_error",
      "message": "Error details",
      "provider": "openai",
      "retry_count": 3,
      "recoverable": true
    }
  }
}
```

### Retry Strategy

1. **Exponential Backoff**: Not implemented (fixed 1s delay)
2. **Max Retries**: 3 attempts
3. **Fallback Chain**: Try next provider on failure
4. **Circuit Breaker**: Not implemented (future enhancement)

## Caching Strategy

### JSON Cache

**Structure**:
```json
{
  "conversations": [
    {
      "timestamp": "2025-01-15T10:30:00Z",
      "user_input": "Create a box",
      "llm_response": "...",
      "provider": "openai",
      "model": "gpt-4o-mini"
    }
  ],
  "design_states": [...],
  "actions_history": [...]
}
```

### SQLite Cache

**Tables**:
- `conversations` - User interactions
- `design_states` - Design snapshots
- `actions_history` - Executed actions

**Queries**:
- `get_recent_conversations(limit)` - Recent chats
- `get_recent_actions(limit)` - Recent executions
- `clear_cache()` - Reset all data

## Security Considerations

### API Key Management

1. **Storage**: config.json (gitignored) or environment variables
2. **Transmission**: HTTPS for API calls (enforced by providers)
3. **Access Control**: Local-only server by default (`allow_remote: false`)

### Input Validation

1. **Pydantic Schemas** - Type checking and validation
2. **Safety Checks** - Dimension validation, unit verification
3. **Action Validation** - Ensure feasible geometry

### Fusion 360 API Safety

1. **Error Handling** - Try/catch around all API calls
2. **User Confirmation** - Optional confirmation before execution
3. **Undo Support** - Fusion's native undo for mistakes

## Performance Optimization

### Async Architecture

- **FastAPI** - Async request handling
- **aiohttp** - Non-blocking HTTP clients
- **Concurrent Requests** - Multiple LLM calls in parallel

### Response Caching

- **Conversation History** - Avoid re-processing same requests
- **Model Results** - Cache for similar prompts (future)

### Request Optimization

- **Prompt Engineering** - Concise, focused prompts
- **JSON Mode** - Direct JSON output (OpenAI)
- **Token Limits** - Configured max_tokens to control costs

## Testing Strategy

### Unit Tests (`tests/`)

- **Schema Tests** - Pydantic model validation
- **Client Tests** - LLM client functionality
- **Cache Tests** - Context cache operations
- **Config Tests** - Configuration loading

### Integration Tests

- **Server Tests** - FastAPI endpoint testing
- **End-to-End Tests** - Full workflow validation

### Manual Testing

- **CLI Tests** - curl commands
- **Fusion Tests** - Interactive testing in Fusion 360

## Deployment

### Local Development

```bash
python -m mcp_server.server
# Server runs on localhost:9000
```

### Production Considerations

1. **Process Manager** - systemd, supervisor, or PM2
2. **Reverse Proxy** - nginx for HTTPS
3. **Monitoring** - Log aggregation, metrics
4. **Scaling** - Multiple worker processes (uvicorn)

### Docker Deployment (Future)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY mcp_server/ ./mcp_server/
COPY prompts/ ./prompts/
CMD ["uvicorn", "mcp_server.server:app", "--host", "0.0.0.0", "--port", "9000"]
```

## Extensibility

### Adding New Actions

1. Define schema in `schema/fusion_action.py`
2. Implement handler in `fusion_actions.py`
3. Update system prompt with examples
4. Add tests

### Adding New LLM Providers

1. Create client in `llm_clients/new_provider.py`
2. Implement `generate()` method
3. Register in `router.py`
4. Update configuration schema

### Custom Workflows

1. Create custom command types in `MCPCommand`
2. Add routing logic in `router.py`
3. Implement handlers in server or add-in

## Future Enhancements

1. **WebSocket Support** - Real-time streaming responses
2. **Multi-Agent System** - Specialized agents for different tasks
3. **Cloud Deployment** - Hosted MCP server
4. **Authentication** - User accounts and API keys
5. **Rate Limiting** - Per-user request limits
6. **Metrics Dashboard** - Usage analytics
7. **Plugin System** - Community extensions

---

**Document Version**: 1.0.0
**Last Updated**: 2025-01-15
