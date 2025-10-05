# Complete Setup Guide - FusionMCP with Ollama

This guide walks you through setting up FusionMCP with Ollama (100% free and offline).

## Why Ollama?

- ✅ **100% Free** - No API costs
- ✅ **Privacy** - Runs locally, data never leaves your computer
- ✅ **Offline** - Works without internet
- ✅ **Fast** - Direct local execution
- ✅ **Easy** - Simple installation

## Step-by-Step Setup

### Step 1: Install Ollama

#### macOS
```bash
# Method 1: Download from website
# Visit https://ollama.com and download Ollama.app
# Drag to Applications folder

# Method 2: Using Homebrew
brew install ollama

# Method 3: Using curl
curl -fsSL https://ollama.com/install.sh | sh
```

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Windows
```bash
# Download from https://ollama.com/download/windows
# Run the installer
# Or use WSL2 and follow Linux instructions
```

### Step 2: Verify Ollama Installation

```bash
# Check if Ollama is installed
ollama --version

# Should show something like:
# ollama version 0.1.20
```

### Step 3: Pull a Model

Ollama needs to download a model first. We recommend `llama3` for best results:

```bash
# Pull Llama 3 (best for CAD tasks)
ollama pull llama3

# Alternative models:
ollama pull mistral        # Faster, smaller
ollama pull codellama      # Good for technical tasks
ollama pull phi            # Smallest, fastest
```

**Model Sizes** (approximate):
- `phi` - 1.6GB (fastest, simplest tasks)
- `mistral` - 4.1GB (good balance)
- `llama3` - 4.7GB (recommended, best quality)
- `codellama` - 7GB (technical focus)

**Note**: First download will take 5-15 minutes depending on your internet speed.

### Step 4: Test Ollama

```bash
# Test the model
ollama run llama3 "What is 2+2?"

# Should respond with "4" or similar

# Exit with Ctrl+D or type /bye
```

### Step 5: Start Ollama Server (Background)

Ollama needs to run as a background service:

#### macOS/Linux
```bash
# Start Ollama server
ollama serve

# Or run in background:
nohup ollama serve > /dev/null 2>&1 &
```

#### Windows
```bash
# Ollama runs automatically as a service after installation
# Check if running:
curl http://localhost:11434
```

**Verify Server**:
```bash
# Should return Ollama version info
curl http://localhost:11434/api/tags
```

### Step 6: Install FusionMCP

#### Clone Repository
```bash
cd ~/Desktop  # or your preferred directory
git clone https://github.com/yourusername/fusion360-mcp.git
cd fusion360-mcp
```

Or download ZIP and extract:
```bash
# If you downloaded the ZIP
cd ~/Downloads
unzip fusion360-mcp-main.zip
cd fusion360-mcp-main
```

#### Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

You should see `(venv)` in your terminal prompt.

#### Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# This will install:
# - FastAPI (web server)
# - Uvicorn (ASGI server)
# - Pydantic (data validation)
# - aiohttp (async HTTP)
# - loguru (logging)
# - and more...
```

### Step 7: Configure for Ollama

#### Create config.json
```bash
# Copy example config
cp examples/example_config.json config.json
```

#### Edit config.json

Open `config.json` in your text editor and modify:

```json
{
  "ollama_url": "http://localhost:11434",
  "default_model": "ollama:llama3",
  "fallback_chain": ["ollama:llama3"],
  "mcp_host": "127.0.0.1",
  "mcp_port": 9000,
  "allow_remote": false,
  "log_level": "INFO",
  "log_dir": "logs",
  "cache_enabled": true,
  "cache_type": "json",
  "cache_path": "context_cache.json",
  "timeout_seconds": 60,
  "max_retries": 3,
  "retry_delay": 1.0,
  "models": {
    "ollama": {
      "available": ["llama3", "mistral", "codellama", "phi"],
      "default": "llama3"
    }
  }
}
```

**Key settings for Ollama**:
- `ollama_url`: Should be `http://localhost:11434`
- `default_model`: Use `"ollama:llama3"` (or your chosen model)
- `fallback_chain`: Just `["ollama:llama3"]` for offline-only setup
- Leave other API keys empty (not needed for Ollama)

### Step 8: Start MCP Server

#### Option 1: Using Helper Script (Easiest)
```bash
# macOS/Linux
./start_server.sh

# Windows
start_server.bat
```

#### Option 2: Direct Command
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or venv\Scripts\activate  # Windows

# Start server
python -m mcp_server.server
```

**Expected Output**:
```
2025-01-15 10:30:00 | INFO     | Logger initialized with level INFO
2025-01-15 10:30:00 | INFO     | Logs will be saved to logs/mcp_server.log
2025-01-15 10:30:00 | INFO     | Created JSON cache at context_cache.json
2025-01-15 10:30:00 | INFO     | Cache initialized: json
2025-01-15 10:30:00 | INFO     | System prompt loaded
2025-01-15 10:30:00 | INFO     | Initialized MCP Router with providers: ['ollama']
2025-01-15 10:30:00 | INFO     | MCP Server started on 127.0.0.1:9000
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:9000 (Press CTRL+C to quit)
```

**✅ Server is ready!** Keep this terminal open.

### Step 9: Test MCP Server

Open a **new terminal** and run:

```bash
# Test 1: Health check
curl http://127.0.0.1:9000/health

# Expected response:
# {"status":"healthy","providers":["ollama"],"cache_enabled":true}

# Test 2: List models
curl http://127.0.0.1:9000/models

# Expected response:
# {"models":{"ollama":["llama3","mistral",...]}}

# Test 3: Ask model to create geometry
curl -X POST http://127.0.0.1:9000/mcp/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "ask_model",
    "params": {
      "provider": "ollama",
      "model": "llama3",
      "prompt": "Create a 20mm cube"
    },
    "context": {
      "active_component": "RootComponent",
      "units": "mm",
      "design_state": "empty"
    }
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "message": "Action generated successfully",
  "actions_to_execute": [
    {
      "action": "create_box",
      "params": {
        "width": 20,
        "height": 20,
        "depth": 20,
        "unit": "mm"
      },
      "explanation": "Creating a 20mm cube",
      "safety_checks": ["dimensions_positive", "units_valid"]
    }
  ],
  "llm_response": {
    "success": true,
    "provider": "ollama",
    "model": "llama3",
    ...
  }
}
```

### Step 10: Install Fusion 360 Add-in

#### Find Fusion Add-ins Folder

**macOS**:
```bash
~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/
```

**Windows**:
```bash
%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\
```

#### Copy Add-in

**macOS**:
```bash
# From fusion360-mcp directory
cp -r fusion_addin ~/Library/Application\ Support/Autodesk/Autodesk\ Fusion\ 360/API/AddIns/FusionMCP

# Verify
ls ~/Library/Application\ Support/Autodesk/Autodesk\ Fusion\ 360/API/AddIns/FusionMCP/
# Should show: main.py, ui_dialog.py, fusion_actions.py, FusionMCP.manifest, utils/
```

**Windows**:
```bash
# From fusion360-mcp directory
xcopy /E /I fusion_addin "%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\FusionMCP"

# Verify
dir "%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\FusionMCP"
```

**Important**: The folder name MUST be `FusionMCP` (case-sensitive).

### Step 11: Load Add-in in Fusion 360

1. **Open/Restart Fusion 360**

2. **Go to Scripts and Add-Ins**:
   - Click **Tools** → **Add-Ins** → **Scripts and Add-Ins**
   - Or press **Shift+S**

3. **Find FusionMCP**:
   - Click **Add-Ins** tab
   - Look for **FusionMCP** in the list
   - If you don't see it, click the **+** (green plus) button and browse to the folder

4. **Run the Add-in**:
   - Select **FusionMCP**
   - Click **Run** button
   - You should see: "FusionMCP Add-in Started! Use the 'MCP Assistant' command..."

5. **Optional - Auto-run on Startup**:
   - Check the **Run on Startup** checkbox
   - Add-in will load automatically next time

### Step 12: Use FusionMCP in Fusion 360

#### Open MCP Assistant

1. Look for **MCP Assistant** button in toolbar
2. Or go to **Tools** menu → Find **MCP Assistant**
3. Click to open the assistant dialog

#### Test Commands

Try these natural language commands:

**Simple Geometry**:
```
Create a 20mm cube
```

**Cylinder**:
```
Make a cylindrical shaft 10mm diameter and 50mm long
```

**Complex Design**:
```
Design a mounting bracket 100x50mm with 4 M5 holes at the corners
```

**With Position**:
```
Create a 5mm hole at position x=25, y=25
```

**Material**:
```
Apply aluminum material to all bodies
```

#### What Happens

1. You type the command
2. Add-in sends to MCP server
3. Ollama (llama3) processes the request
4. Returns structured JSON action
5. Add-in executes in Fusion 360
6. Geometry appears!

### Step 13: Monitor and Debug

#### Check MCP Server Logs
```bash
# View logs in real-time
tail -f logs/mcp_server.log

# Or open in text editor
cat logs/mcp_server.log
```

#### Check Conversation History
```bash
# View cached conversations
curl http://127.0.0.1:9000/history?limit=5
```

#### Debug Issues

**Issue**: "Connection refused"
```bash
# Make sure MCP server is running
curl http://127.0.0.1:9000/health

# If not working, restart server
python -m mcp_server.server
```

**Issue**: "Ollama not found"
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

**Issue**: "Model not found"
```bash
# Pull the model again
ollama pull llama3

# List available models
ollama list
```

## Complete Startup Checklist

Every time you want to use FusionMCP:

### Terminal 1 - Ollama (if not auto-running)
```bash
ollama serve
```

### Terminal 2 - MCP Server
```bash
cd ~/Desktop/fusion360-mcp  # or your path
source venv/bin/activate
python -m mcp_server.server
```

### Fusion 360
1. Open Fusion 360
2. Load FusionMCP add-in (if not auto-run)
3. Click MCP Assistant
4. Start designing!

## Performance Tips

### Faster Response Times

1. **Use Smaller Models** (if llama3 is slow):
   ```bash
   ollama pull phi  # Smallest, fastest
   ```

   Update `config.json`:
   ```json
   "default_model": "ollama:phi"
   ```

2. **Lower Temperature** (more consistent):
   ```json
   "temperature": 0.3  // More precise, less creative
   ```

3. **Reduce Max Tokens**:
   ```json
   "max_tokens": 1000  // Faster responses
   ```

### GPU Acceleration

Ollama automatically uses GPU if available:

```bash
# Check GPU usage (macOS)
sudo powermetrics --samplers gpu_power

# Check GPU usage (Linux with nvidia)
nvidia-smi

# Check GPU usage (Windows)
# Task Manager → Performance → GPU
```

### Memory Management

Large models use RAM:
- `phi`: ~2GB RAM
- `llama3`: ~6GB RAM
- `codellama`: ~8GB RAM

If slow, use smaller model or close other apps.

## Example Workflows

### Workflow 1: Simple Box
```
User: "Create a 50mm cube"
→ Ollama generates: {"action": "create_box", "params": {"width": 50, ...}}
→ Fusion creates 50x50x50mm box
⏱️ Time: ~3-5 seconds
```

### Workflow 2: Mounting Bracket
```
User: "Design a mounting plate 100x50mm with 4 holes"
→ Ollama generates action sequence:
  1. Create base plate 100x50x5mm
  2. Add hole 1 at (10,10)
  3. Add hole 2 at (90,10)
  4. Add hole 3 at (10,40)
  5. Add hole 4 at (90,40)
→ Fusion executes all 5 actions
⏱️ Time: ~8-12 seconds
```

### Workflow 3: Parametric Design
```
User: "Create a shaft where diameter is 1/5 of the length, length 100mm"
→ Ollama calculates: diameter = 100/5 = 20mm
→ Generates: {"action": "create_cylinder", "params": {"radius": 10, "height": 100}}
→ Fusion creates 20mm diameter x 100mm shaft
⏱️ Time: ~5-8 seconds
```

## Troubleshooting

### Common Issues

#### 1. MCP Server Won't Start

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 9000
lsof -i :9000  # macOS/Linux
netstat -ano | findstr :9000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or change port in config.json
"mcp_port": 9001
```

#### 2. Ollama Connection Failed

**Error**: `Connection refused to localhost:11434`

**Solution**:
```bash
# Start Ollama server
ollama serve

# Or check if it's running
ps aux | grep ollama  # macOS/Linux
tasklist | findstr ollama  # Windows
```

#### 3. Slow Responses

**Solution**:
```bash
# Use faster model
ollama pull phi
# Update config.json: "default_model": "ollama:phi"

# Or reduce max_tokens
# In config.json: "max_tokens": 500
```

#### 4. Fusion Add-in Not Visible

**Solution**:
- Verify folder name is exactly `FusionMCP`
- Check manifest file exists: `FusionMCP.manifest`
- Restart Fusion 360
- Try manual add: Scripts & Add-Ins → + → Browse to folder

#### 5. Import Errors in Python

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. **Try More Models**:
   ```bash
   ollama pull mistral
   ollama pull codellama
   ```

2. **Customize System Prompt**:
   - Edit `prompts/system_prompt.md`
   - Adjust behavior and output format

3. **Add API Keys** (optional, for cloud models):
   - Edit `config.json`
   - Add OpenAI/Gemini/Claude keys
   - Enable fallback chain

4. **Explore Examples**:
   - Check `examples/test_conversation.json`
   - Try example commands

5. **Run Tests**:
   ```bash
   ./run_tests.sh
   # or
   pytest tests/ -v
   ```

## Quick Reference

### Essential Commands

```bash
# Start Ollama
ollama serve

# Pull model
ollama pull llama3

# Activate venv
source venv/bin/activate

# Start MCP server
python -m mcp_server.server

# Test server
curl http://127.0.0.1:9000/health

# View logs
tail -f logs/mcp_server.log

# Run tests
pytest tests/ -v
```

### File Locations

```
~/Desktop/fusion360-mcp/              # Project root
├── config.json                        # Your config
├── venv/                              # Virtual environment
├── logs/mcp_server.log               # Server logs
└── context_cache.json                # Conversation history

~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/FusionMCP/
                                      # Fusion add-in (macOS)

%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\FusionMCP\
                                      # Fusion add-in (Windows)
```

## Success Checklist

- [ ] Ollama installed and running
- [ ] Model downloaded (llama3 or phi)
- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] config.json configured for Ollama
- [ ] MCP server running (http://127.0.0.1:9000)
- [ ] Health check passes (`curl http://127.0.0.1:9000/health`)
- [ ] Fusion add-in copied to correct folder
- [ ] Fusion add-in loaded and running
- [ ] MCP Assistant button visible in Fusion
- [ ] Test command works ("Create a 20mm cube")

## 🎉 You're Ready!

Once all checkboxes are ✅, you can:

- Design with natural language
- Create parametric CAD models
- Use AI for geometric reasoning
- Work 100% offline and free
- Maintain complete privacy

**Have fun building with FusionMCP + Ollama!** 🚀

---

**Need Help?** Check README.md or open an issue on GitHub
