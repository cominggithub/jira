#!/usr/bin/env python3
"""
Test script for MCP demo server
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server():
    """Test the MCP server by sending some basic requests."""
    
    print("🚀 Testing MCP Demo Server")
    print("=" * 50)
    
    # Start the server process
    server_process = subprocess.Popen(
        [sys.executable, "mcp_demo_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Test initialization
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialization request...")
        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"📥 Initialization response: {json.dumps(response, indent=2)}")
        
        # Test list tools
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        print("\n📤 Requesting available tools...")
        server_process.stdin.write(json.dumps(list_tools_request) + "\n")
        server_process.stdin.flush()
        
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"📥 Tools list response: {json.dumps(response, indent=2)}")
        
        print("\n✅ MCP Server test completed!")
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        
    finally:
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())