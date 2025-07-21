#!/usr/bin/env python3
"""
Direct test of MCP server functions
"""

import sys
import os
sys.path.append('.')

# Import the MCP server and call functions directly
from mcp_demo_server import call_tool
import asyncio

async def test_get_system_info():
    """Test the get_system_info tool directly."""
    
    print("🚀 Testing get_system_info tool directly")
    print("=" * 50)
    
    try:
        # Call the tool directly
        result = await call_tool("get_system_info", {})
        
        print("✅ Tool call successful!")
        print("📋 Result:")
        
        # Print the content
        for content_item in result.content:
            if hasattr(content_item, 'text'):
                print(content_item.text)
            elif hasattr(content_item, 'type') and content_item.type == 'text':
                print(content_item.text if hasattr(content_item, 'text') else str(content_item))
            else:
                print(str(content_item))
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_list_files():
    """Test the list_files tool directly."""
    
    print("\n🚀 Testing list_files tool directly")
    print("=" * 50)
    
    try:
        # Call the tool directly
        result = await call_tool("list_files", {"path": "."})
        
        print("✅ Tool call successful!")
        print("📋 Result:")
        
        # Print the content
        for content_item in result.content:
            if hasattr(content_item, 'text'):
                print(content_item.text)
            else:
                print(str(content_item))
                
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_write_demo_file():
    """Test the write_demo_file tool directly."""
    
    print("\n🚀 Testing write_demo_file tool directly")
    print("=" * 50)
    
    try:
        # Call the tool directly
        result = await call_tool("write_demo_file", {
            "filename": "mcp_test_output.txt",
            "content": "Hello from MCP server! This file was created by calling the get_system_info tool."
        })
        
        print("✅ Tool call successful!")
        print("📋 Result:")
        
        # Print the content
        for content_item in result.content:
            if hasattr(content_item, 'text'):
                print(content_item.text)
            else:
                print(str(content_item))
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_get_system_info())
    asyncio.run(test_list_files())
    asyncio.run(test_write_demo_file())