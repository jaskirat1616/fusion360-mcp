# Fusion 360 MCP - Multi-Model AI Integration

**FusionMCP** is a comprehensive Model Context Protocol (MCP) integration layer that connects Autodesk Fusion 360 with multiple AI backends (Ollama, OpenAI, Google Gemini, and Anthropic Claude) to enable AI-powered parametric CAD design through natural language.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Fusion 360](https://img.shields.io/badge/Fusion%20360-2025-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 🎯 Features

- 🤖 **Multi-Model Support**: Seamlessly switch between Ollama, OpenAI GPT-4o, Google Gemini, and Claude 3.5
- 🔄 **Intelligent Routing**: Automatic fallback chain when primary model fails
- 📐 **Parametric Design**: AI understands and generates parametric CAD operations
- 🛡️ **Safety First**: Built-in validation for dimensions, units, and geometric feasibility
- 💾 **Context Caching**: Conversation and design state persistence (JSON/SQLite)
- 🎨 **Fusion 360 Integration**: Native add-in for seamless workflow
- ⚡ **Async Architecture**: Fast, non-blocking operations with retry logic
- 📊 **Structured Logging**: Detailed logs with Loguru

## 📋 Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Model Comparison](#model-comparison)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Fusion 360 User                         │
│                           ↓                                 │
│              ┌─────────────────────────┐                    │
│              │  Fusion 360 Add-in      │                    │
│              │  - UI Dialog            │                    │
│              │  - Action Executor      │                    │
│              │  - Network Client       │                    │
│              └──────────┬──────────────┘                    │
│                         ↓ HTTP/REST                         │
│              ┌─────────────────────────┐                    │
│              │   MCP Server (FastAPI)  │                    │
│              │  - Router               │                    │
│              │  - Schema Validation    │                    │
│              │  - Context Cache        │                    │
│              └──────────┬──────────────┘                    │
│                         ↓                                    │
│         ┌───────────────┴───────────────────┐               │
│         ↓               ↓           ↓       ↓               │
│   ┌─────────┐   ┌──────────┐  ┌────────┐  ┌──────────┐     │
│   │ Ollama  │   │  OpenAI  │  │ Gemini │  │  Claude  │     │
│   │ (Local) │   │   API    │  │  API   │  │   API    │     │
│   └─────────┘   └──────────┘  └────────┘  └──────────┘     │
│                                                              │
│              System Prompt (FusionMCP Personality)          │
│              ↓                                              │
│         Structured JSON Actions → Fusion 360                │
└─────────────────────────────────────────────────────────────┘
```

### Component Overview

1. **Fusion 360 Add-in** (`fusion_addin/`)
   - Python-based Fusion 360 add-in
   - Captures user intent and design context
   - Executes structured CAD actions
   - Real-time UI feedback

2. **MCP Server** (`mcp_server/`)
   - FastAPI-based REST server
   - Routes requests to appropriate LLM
   - Validates and normalizes responses
   - Caches conversation history

3. **LLM Clients** (`mcp_server/llm_clients/`)
   - Unified interface for all models
   - Provider-specific implementations
   - Automatic retry and error handling

4. **System Prompt** (`prompts/system_prompt.md`)
   - Defines FusionMCP personality
   - Enforces JSON output format
   - Provides action schema templates

## 🚀 Installation

### Prerequisites

- **Python 3.11+** (for MCP server)
- **Autodesk Fusion 360** (2025 version recommended)
- **At least one LLM provider**:
  - [Ollama](https://ollama.ai) (local, free)
  - [OpenAI API Key](https://platform.openai.com)
  - [Google AI API Key](https://makersuite.google.com/app/apikey)
  - [Anthropic API Key](https://console.anthropic.com)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/fusion360-mcp.git
cd fusion360-mcp
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Step 3: Configure Environment

Create `config.json` from example:

```bash
cp examples/example_config.json config.json
```

Edit `config.json` with your API keys:

```json
{
  "ollama_url": "http://localhost:11434",
  "openai_api_key": "sk-proj-...",
  "gemini_api_key": "AIza...",
  "claude_api_key": "sk-ant-...",
  "default_model": "openai:gpt-4o-mini",
  "mcp_host": "127.0.0.1",
  "mcp_port": 9000
}
```

**Alternative**: Use environment variables (`.env` file):

```bash
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIza...
CLAUDE_API_KEY=sk-ant-...
```

### Step 4: Install Fusion 360 Add-in

1. Copy `fusion_addin/` folder to Fusion 360 add-ins directory:
   - **Windows**: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`
   - **macOS**: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`

2. Rename to `FusionMCP`:
   ```bash
   cp -r fusion_addin "/Users/YOUR_USER/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/FusionMCP"
   ```

3. Restart Fusion 360

4. Open Fusion 360 → **Scripts and Add-Ins** → **Add-Ins** tab → Select **FusionMCP** → **Run**

## 🎬 Quick Start

### 1. Start MCP Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start server
python -m mcp_server.server
```

Expected output:
```
INFO     | Logger initialized with level INFO
INFO     | Cache initialized: json
INFO     | System prompt loaded
INFO     | Initialized MCP Router with providers: ['ollama', 'openai', 'gemini', 'claude']
INFO     | MCP Server started on 127.0.0.1:9000
```

### 2. Test Server (Optional)

```bash
curl -X POST http://127.0.0.1:9000/mcp/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "ask_model",
    "params": {
      "provider": "openai",
      "model": "gpt-4o-mini",
      "prompt": "Create a 20mm cube"
    },
    "context": {
      "active_component": "RootComponent",
      "units": "mm",
      "design_state": "empty"
    }
  }'
```

### 3. Use in Fusion 360

1. Open Fusion 360
2. Click **Scripts and Add-Ins** → **Add-Ins** → **FusionMCP** → **Run**
3. Click **MCP Assistant** button in toolbar
4. Enter natural language command:
   - "Create a 20mm cube"
   - "Design a mounting bracket with 4 holes"
   - "Make a cylindrical shaft 10mm diameter, 50mm long"

## ⚙️ Configuration

### Full Configuration Options

```json
{
  // API Configuration
  "ollama_url": "http://localhost:11434",
  "openai_api_key": "sk-proj-...",
  "gemini_api_key": "AIza...",
  "claude_api_key": "sk-ant-...",

  // Model Selection
  "default_model": "openai:gpt-4o-mini",
  "fallback_chain": [
    "openai:gpt-4o-mini",
    "gemini:gemini-1.5-flash-latest",
    "ollama:llama3"
  ],

  // Server Settings
  "mcp_host": "127.0.0.1",
  "mcp_port": 9000,
  "allow_remote": false,

  // Logging
  "log_level": "INFO",
  "log_dir": "logs",

  // Caching
  "cache_enabled": true,
  "cache_type": "json",  // or "sqlite"
  "cache_path": "context_cache.json",

  // Timeouts and Retries
  "timeout_seconds": 30,
  "max_retries": 3,
  "retry_delay": 1.0,

  // Available Models
  "models": {
    "ollama": {
      "available": ["llama3", "mistral", "codellama"],
      "default": "llama3"
    },
    "openai": {
      "available": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
      "default": "gpt-4o-mini"
    },
    "gemini": {
      "available": ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest"],
      "default": "gemini-1.5-flash-latest"
    },
    "claude": {
      "available": ["claude-3-5-sonnet-20241022"],
      "default": "claude-3-5-sonnet-20241022"
    }
  }
}
```

## 💡 Usage Examples

### Example 1: Simple Geometry

**Prompt**: "Create a 20mm cube"

**Generated Action**:
```json
{
  "action": "create_box",
  "params": {
    "width": 20,
    "height": 20,
    "depth": 20,
    "unit": "mm"
  },
  "explanation": "Creating a 20mm cubic box",
  "safety_checks": ["dimensions_positive", "units_valid"]
}
```

### Example 2: Complex Design

**Prompt**: "Design a mounting bracket 100x50mm with 4 M5 mounting holes"

**Generated Action Sequence**:
```json
{
  "actions": [
    {
      "action": "create_box",
      "params": {"width": 100, "height": 50, "depth": 5, "unit": "mm"},
      "explanation": "Create base plate"
    },
    {
      "action": "create_hole",
      "params": {"diameter": 5.5, "position": {"x": 10, "y": 10}, "unit": "mm"},
      "explanation": "M5 clearance hole (10mm edge offset)"
    },
    // ... 3 more holes
  ],
  "total_steps": 5
}
```

### Example 3: Parametric Design

**Prompt**: "Create a shaft with diameter 2x of length"

```json
{
  "clarifying_questions": [
    {
      "question": "What is the shaft length?",
      "context": "Need length to calculate diameter (diameter = 2 × length)",
      "suggestions": ["50mm", "100mm", "Custom"]
    }
  ]
}
```

## 📡 API Reference

### Endpoints

#### POST `/mcp/command`

Execute MCP command.

**Request Body**:
```json
{
  "command": "ask_model",
  "params": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "prompt": "User prompt here",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "context": {
    "active_component": "RootComponent",
    "units": "mm",
    "design_state": "empty"
  }
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Action generated successfully",
  "actions_to_execute": [...],
  "llm_response": {...}
}
```

#### GET `/health`

Health check.

**Response**:
```json
{
  "status": "healthy",
  "providers": ["ollama", "openai", "gemini", "claude"],
  "cache_enabled": true
}
```

#### GET `/models`

List available models.

**Response**:
```json
{
  "models": {
    "ollama": ["llama3", "mistral"],
    "openai": ["gpt-4o", "gpt-4o-mini"],
    "gemini": ["gemini-1.5-pro-latest"],
    "claude": ["claude-3-5-sonnet-20241022"]
  }
}
```

#### GET `/history?limit=10`

Get conversation history.

**Response**:
```json
{
  "conversations": [...],
  "actions": [...]
}
```

### Supported Actions

| Action | Description | Required Params |
|--------|-------------|-----------------|
| `create_box` | Create rectangular box | `width`, `height`, `depth`, `unit` |
| `create_cylinder` | Create cylinder | `radius`, `height`, `unit` |
| `create_sphere` | Create sphere | `radius`, `unit` |
| `create_hole` | Create hole | `diameter`, `position`, `unit` |
| `extrude` | Extrude profile | `profile`, `distance`, `unit` |
| `fillet` | Round edges | `edges`, `radius`, `unit` |
| `apply_material` | Apply material | `material_name` |

## 🔬 Model Comparison

| Feature | Ollama (Local) | OpenAI GPT-4o | Google Gemini | Claude 3.5 |
|---------|---------------|---------------|---------------|------------|
| **Cost** | Free | $$ | $ | $$$ |
| **Speed** | Fast | Medium | Fast | Medium |
| **Offline** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **JSON Mode** | Limited | ✅ Native | Good | Good |
| **Reasoning** | Good | Excellent | Very Good | Excellent |
| **Geometry** | Good | Very Good | Excellent | Very Good |
| **Creative** | Good | Excellent | Very Good | Good |
| **Best For** | Privacy, Offline | Creative designs | Spatial reasoning | Safety validation |

### Recommended Workflows

1. **Creative Design**: OpenAI GPT-4o → Claude (validation)
2. **Geometric Precision**: Gemini → OpenAI
3. **Privacy-First**: Ollama (all tasks)
4. **Cost-Optimized**: Gemini Flash → Ollama (fallback)

## 🛠️ Development

### Project Structure

```
fusion360-mcp/
├── mcp_server/                 # MCP Server
│   ├── server.py              # FastAPI app
│   ├── router.py              # Request routing
│   ├── schema/                # Pydantic models
│   ├── llm_clients/           # LLM implementations
│   └── utils/                 # Utilities
├── fusion_addin/              # Fusion 360 Add-in
│   ├── main.py                # Entry point
│   ├── ui_dialog.py           # UI components
│   ├── fusion_actions.py      # Action executor
│   └── utils/network.py       # Network client
├── prompts/                   # System prompts
├── examples/                  # Example configs
├── tests/                     # Test suite
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_mcp_server.py -v

# Run with coverage
pytest tests/ --cov=mcp_server --cov-report=html
```

### Adding New LLM Provider

1. Create client in `mcp_server/llm_clients/new_provider_client.py`:

```python
class NewProviderClient:
    async def generate(self, model, prompt, system_prompt, temperature, max_tokens):
        # Implementation
        return {
            "provider": "new_provider",
            "model": model,
            "output": "...",
            "json": {...},
            "tokens_used": 123
        }
```

2. Register in `router.py`:

```python
if config.new_provider_api_key:
    self.clients["new_provider"] = NewProviderClient(...)
```

### Code Style

- **PEP8** compliant
- **Type annotations** required
- **Docstrings** for all functions/classes
- **Async/await** for I/O operations

## 🐛 Troubleshooting

### Common Issues

#### 1. Server Won't Start

**Error**: `Address already in use`

**Solution**: Change port in `config.json`:
```json
{"mcp_port": 9001}
```

#### 2. Fusion Add-in Not Visible

**Solution**:
- Verify add-in is in correct folder
- Check `FusionMCP.manifest` exists
- Restart Fusion 360
- Check **Scripts and Add-Ins** → **Add-Ins** tab

#### 3. API Key Errors

**Error**: `401 Unauthorized`

**Solution**:
- Verify API key in `config.json`
- Check key has proper permissions
- Try environment variables instead

#### 4. Ollama Connection Failed

**Error**: `Connection refused`

**Solution**:
```bash
# Check Ollama is running
ollama list

# Start Ollama service
ollama serve
```

#### 5. JSON Parsing Errors

**Solution**:
- Check system prompt is loaded
- Verify model supports JSON mode
- Use temperature < 0.8 for better structure
- Enable `json_mode=True` in OpenAI client

### Debug Mode

Enable verbose logging:

```json
{"log_level": "DEBUG"}
```

Check logs in `logs/mcp_server.log`

### Health Check

```bash
# Check server health
curl http://127.0.0.1:9000/health

# List available models
curl http://127.0.0.1:9000/models

# View conversation history
curl http://127.0.0.1:9000/history?limit=5
```

## 🧪 Testing the System

### Manual CLI Test

```bash
curl -X POST http://127.0.0.1:9000/mcp/command \
  -H "Content-Type: application/json" \
  -d @examples/example_command.json
```

### Python Test Script

```python
import requests

command = {
    "command": "ask_model",
    "params": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "prompt": "Create a 10mm cube"
    },
    "context": {
        "units": "mm",
        "design_state": "empty"
    }
}

response = requests.post("http://127.0.0.1:9000/mcp/command", json=command)
print(response.json())
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run linting
ruff check mcp_server/
black mcp_server/
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- Autodesk Fusion 360 API
- FastAPI framework
- Anthropic, OpenAI, Google for LLM APIs
- Ollama for local LLM support

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/fusion360-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/fusion360-mcp/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/fusion360-mcp/wiki)

## 🗺️ Roadmap

- [ ] WebSocket streaming for real-time chat
- [ ] Multi-agent orchestration
- [ ] Generative Design API integration
- [ ] Geometry export to Markdown/docs
- [ ] Fusion 360 UI palette integration
- [ ] 3D preview before execution
- [ ] Undo/redo action history
- [ ] Cloud deployment support

---

**Built with ❤️ for the Fusion 360 and AI community**
