# FusionMCP Quick Start Guide

Get up and running with FusionMCP in 5 minutes!

## 📋 Prerequisites

- Python 3.11+
- Fusion 360 (2025)
- At least one AI provider (Ollama recommended for beginners)

## 🚀 5-Minute Setup

### Step 1: Install Ollama (Easiest Option)

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com

# Pull a model
ollama pull llama3
```

### Step 2: Clone and Install

```bash
# Clone repository
git clone https://github.com/yourusername/fusion360-mcp.git
cd fusion360-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure

```bash
# Copy example config
cp examples/example_config.json config.json

# Edit config.json - for Ollama only, just verify:
# "default_model": "ollama:llama3"
```

### Step 4: Start Server

```bash
# Option 1: Use helper script
./start_server.sh  # or start_server.bat on Windows

# Option 2: Direct command
python -m mcp_server.server
```

You should see:
```
✅ Logger initialized with level INFO
✅ Initialized MCP Router with providers: ['ollama']
✅ MCP Server started on 127.0.0.1:9000
```

### Step 5: Install Fusion Add-in

**macOS**:
```bash
cp -r fusion_addin ~/Library/Application\ Support/Autodesk/Autodesk\ Fusion\ 360/API/AddIns/FusionMCP
```

**Windows**:
```bash
xcopy /E /I fusion_addin "%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\FusionMCP"
```

### Step 6: Test in Fusion 360

1. Open/Restart Fusion 360
2. Go to **Tools** → **Add-Ins** → **Scripts and Add-Ins**
3. Select **FusionMCP** → Click **Run**
4. Click the **MCP Assistant** button in toolbar
5. Try these commands:

```
Create a 20mm cube
Design a mounting bracket with 4 holes
Make a cylindrical shaft 10mm diameter, 50mm long
```

## ✅ Verify Installation

### Test Server (Terminal)

```bash
# Health check
curl http://127.0.0.1:9000/health

# Test command
curl -X POST http://127.0.0.1:9000/mcp/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "ask_model",
    "params": {
      "provider": "ollama",
      "model": "llama3",
      "prompt": "Create a 10mm cube"
    }
  }'
```

Expected response:
```json
{
  "status": "success",
  "actions_to_execute": [
    {
      "action": "create_box",
      "params": {"width": 10, "height": 10, "depth": 10, "unit": "mm"}
    }
  ]
}
```

## 🔧 Adding More Providers

### OpenAI (Recommended for Production)

1. Get API key from https://platform.openai.com
2. Edit `config.json`:

```json
{
  "openai_api_key": "sk-proj-YOUR_KEY_HERE",
  "default_model": "openai:gpt-4o-mini"
}
```

3. Restart server

### Google Gemini (Fast & Affordable)

1. Get API key from https://makersuite.google.com/app/apikey
2. Edit `config.json`:

```json
{
  "gemini_api_key": "AIza_YOUR_KEY_HERE",
  "default_model": "gemini:gemini-1.5-flash-latest"
}
```

### Claude (Best Reasoning)

1. Get API key from https://console.anthropic.com
2. Edit `config.json`:

```json
{
  "claude_api_key": "sk-ant-YOUR_KEY_HERE",
  "default_model": "claude:claude-3-5-sonnet-20241022"
}
```

## 🎯 Example Workflows

### Simple Geometry
```
User: "Create a 50mm cube"
→ Creates 50x50x50mm box
```

### Complex Design
```
User: "Design a phone stand"
→ AI asks clarifying questions about dimensions
→ Generates multi-step design with base, support, and angle
```

### Parametric Design
```
User: "Make a mounting bracket 100x50mm with 4 M5 holes at corners"
→ Creates base plate 100x50x5mm
→ Adds 4x 5.5mm holes with 10mm edge offset
```

## 🐛 Common Issues

### Issue: "Connection refused"
**Solution**: Make sure MCP server is running (`python -m mcp_server.server`)

### Issue: "Ollama not found"
**Solution**: Install Ollama and verify with `ollama list`

### Issue: "Add-in not visible in Fusion"
**Solution**:
- Check folder name is exactly `FusionMCP`
- Restart Fusion 360
- Verify path: Scripts and Add-Ins → Add-Ins tab

### Issue: "API key invalid"
**Solution**:
- Verify key in config.json
- Check no extra spaces or quotes
- Try .env file instead

## 📚 Next Steps

1. **Read Full Docs**: See [README.md](README.md) for complete documentation
2. **Explore Examples**: Check `examples/` folder for more use cases
3. **Customize System Prompt**: Edit `prompts/system_prompt.md` for behavior changes
4. **Join Community**: Star on GitHub, join discussions

## 💡 Pro Tips

1. **Use Fallback Chain** for reliability:
   ```json
   "fallback_chain": [
     "openai:gpt-4o-mini",
     "gemini:gemini-1.5-flash-latest",
     "ollama:llama3"
   ]
   ```

2. **Enable Caching** for conversation history:
   ```json
   "cache_enabled": true,
   "cache_type": "json"
   ```

3. **Adjust Temperature** for precision:
   - `0.3-0.5`: Precise, predictable (engineering)
   - `0.7-0.9`: Creative, varied (design exploration)

4. **Check Logs** when debugging:
   ```bash
   tail -f logs/mcp_server.log
   ```

## 🎉 Success!

You're now ready to use AI-powered parametric CAD design!

Try asking: *"Design a custom enclosure for a 50x30x20mm PCB with mounting tabs"*

---

**Need Help?** Open an issue on GitHub or check the troubleshooting guide in README.md
