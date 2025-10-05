@echo off
REM Start FusionMCP Server (Windows)

echo Starting FusionMCP Server...

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Check if config exists
if not exist config.json (
    echo config.json not found! Copying from example...
    copy examples\example_config.json config.json
    echo Please edit config.json with your API keys
    pause
    exit /b 1
)

REM Start server
python -m mcp_server.server

echo Server stopped
pause
