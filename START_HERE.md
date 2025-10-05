# 🚀 START HERE - Quick Setup Guide

## ✅ Setup Complete!

Everything is configured and ready to use with Ollama (your local models).

---

## 📋 How to Run FusionMCP

### **Step 1: Start Ollama Server**

Open **Terminal 1**:
```bash
ollama serve
```

Leave this running. You should see:
```
Ollama is running
```

---

### **Step 2: Start MCP Server**

Open **Terminal 2**:
```bash
cd ~/Desktop/fusion360-mcp
source venv/bin/activate
python -m mcp_server.server
```

You should see:
```
✅ Logger initialized with level INFO
✅ System prompt loaded
✅ Initialized MCP Router with providers: ['ollama']
✅ MCP Server started on 127.0.0.1:9000
```

Leave this running!

---

### **Step 3: Open Fusion 360**

1. **Launch Fusion 360**

2. **Load the Add-in**:
   - Press **Shift + S** (or Tools → Add-Ins → Scripts and Add-Ins)
   - Click **Add-Ins** tab
   - Find **FusionMCP** in the list
   - Select it and click **Run**

3. **You should see**: "FusionMCP Add-in Started!"

4. **Optional**: Check "Run on Startup" to auto-load next time

---

### **Step 4: Use MCP Assistant**

1. Look for **MCP Assistant** button in Fusion 360 toolbar

2. Click it to open the assistant

3. **Try these commands**:
   ```
   Create a 20mm cube
   ```

   ```
   Make a cylindrical shaft 10mm diameter and 50mm long
   ```

   ```
   Design a mounting bracket 100x50mm with 4 M5 holes at corners
   ```

4. Watch the magic happen! 🎉

---

## 🎯 Your Configuration

**Model**: llama3.1:latest (your best local model)
**Fallback**: phi4-mini (if llama3.1 fails)
**Server**: http://localhost:9000
**Mode**: 100% Local & Offline

---

## 🐛 Troubleshooting

### Issue: "Connection refused"
```bash
# Make sure MCP server is running
curl http://127.0.0.1:9000/health
# Should return: {"status":"healthy","providers":["ollama"]...}
```

### Issue: "Ollama not found"
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags
# Should return list of models
```

### Issue: Add-in not visible in Fusion
1. Restart Fusion 360
2. Check folder name is exactly `FusionMCP`
3. Go to Tools → Add-Ins → Scripts and Add-Ins → Add-Ins tab

### Issue: Slow responses
```bash
# Use faster model - edit config.json:
"default_model": "ollama:phi4-mini"
```

---

## 📊 Check Server Status

```bash
# Health check
curl http://127.0.0.1:9000/health

# List available models
curl http://127.0.0.1:9000/models

# View conversation history
curl http://127.0.0.1:9000/history?limit=5
```

---

## 📚 Documentation

- **Full Setup Guide**: `SETUP_OLLAMA.md`
- **Quick Start**: `QUICKSTART.md`
- **Complete Docs**: `README.md`
- **Architecture**: `ARCHITECTURE.md`

---

## 🎨 Your Available Models

Based on your Ollama installation:
- **llama3.1** - Best quality (default)
- **phi4-mini** - Fast & small
- **gemma3** - Good balance
- **qwen3-coder** - Code-focused

To switch models, edit `config.json`:
```json
"default_model": "ollama:phi4-mini"
```

---

## ✅ Quick Checklist

Before testing:
- [ ] Ollama running (`ollama serve`)
- [ ] MCP server running (`python -m mcp_server.server`)
- [ ] Fusion 360 open
- [ ] FusionMCP add-in loaded
- [ ] MCP Assistant button visible

---

## 🎉 You're Ready!

Everything is configured to use **your new FusionMCP system** with:
- ✅ Multi-model architecture
- ✅ Intelligent fallback chain
- ✅ Complete logging & caching
- ✅ Production-ready code
- ✅ Full test suite

**Next**: Open Fusion 360 and start designing with AI! 🚀

---

**Questions?** Check the docs or run tests:
```bash
./run_tests.sh
```
