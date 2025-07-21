#!/usr/bin/env python3
"""
Script to call MCP server tools directly
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def call_mcp_tool(tool_name, arguments=None):
    """Call a specific MCP tool and return the result."""
    
    if arguments is None:
        arguments = {}
    
    print(f"🔧 Calling MCP tool: {tool_name}")
    print(f"📝 Arguments: {arguments}")
    print("-" * 50)
    
    # Start the MCP server process
    server_process = subprocess.Popen(
        [sys.executable, "mcp_demo_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Initialize the server
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
        
        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        
        # Read initialization response
        init_response = server_process.stdout.readline()
        if init_response:
            init_result = json.loads(init_response.strip())
            print(f"✅ Server initialized: {init_result.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        
        # Send the tool call request
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        server_process.stdin.write(json.dumps(tool_request) + "\n")
        server_process.stdin.flush()
        
        # Read the tool response
        tool_response = server_process.stdout.readline()
        if tool_response:
            result = json.loads(tool_response.strip())
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print("✅ Tool call successful!")
                print("📋 Result:")
                
                # Extract content from the result
                content = result.get('result', {}).get('content', [])
                for item in content:
                    if item.get('type') == 'text':
                        print(item.get('text', ''))
                    
                return result
        else:
            print("❌ No response from server")
            
    except Exception as e:
        print(f"❌ Error calling MCP tool: {e}")
        
    finally:
        server_process.terminate()
        server_process.wait()

async def main():
    """Main function to test various MCP tools."""
    
    print("🚀 MCP Tool Testing")
    print("=" * 60)
    
    # Test get_system_info
    await call_mcp_tool("get_system_info")
    
    print("\n" + "=" * 60)
    
    # Test list_files
    await call_mcp_tool("list_files", {"path": "."})
    
    print("\n" + "=" * 60)
    
    # Test write_demo_file
    await call_mcp_tool("write_demo_file", {
        "filename": "mcp_test_output.txt",
        "content": "This is a test file created by MCP server!"
    })

if __name__ == "__main__":
    asyncio.run(main())