"""
Network utilities for MCP communication
"""

import json
import urllib.request
import urllib.error


class MCPClient:
    """Client for communicating with MCP server"""

    def __init__(self, host: str = "127.0.0.1", port: int = 9000):
        """
        Initialize MCP client

        Args:
            host: MCP server host
            port: MCP server port
        """
        self.base_url = f"http://{host}:{port}"

    def send_command(self, command: dict) -> dict:
        """
        Send command to MCP server

        Args:
            command: Command dictionary

        Returns:
            Response dictionary
        """
        url = f"{self.base_url}/mcp/command"

        # Convert to JSON
        data = json.dumps(command).encode('utf-8')

        # Create request
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        try:
            # Send request
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result

        except urllib.error.HTTPError as e:
            return {
                "status": "error",
                "message": f"HTTP {e.code}: {e.reason}"
            }
        except urllib.error.URLError as e:
            return {
                "status": "error",
                "message": f"Connection failed: {e.reason}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Request failed: {str(e)}"
            }

    def check_health(self) -> dict:
        """Check MCP server health"""
        url = f"{self.base_url}/health"

        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return json.loads(response.read().decode('utf-8'))
        except:
            return {"status": "unreachable"}

    def list_models(self) -> dict:
        """List available models"""
        url = f"{self.base_url}/models"

        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except:
            return {"models": {}}
