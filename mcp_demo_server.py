#!/usr/bin/env python3
"""
Simple MCP Server Demo
This demonstrates a basic MCP server with file operations and system info tools.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import mcp.server.stdio


# Create the server instance
server = Server("demo-server")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="get_system_info",
                description="Get basic system information",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="list_files",
                description="List files in a directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list (defaults to current directory)",
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name="read_file",
                description="Read contents of a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to read",
                        }
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="write_demo_file",
                description="Write a demo file with current timestamp",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the demo file to create",
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file",
                        }
                    },
                    "required": ["filename"],
                },
            ),
        ]
    )


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    
    if name == "get_system_info":
        import platform
        import os
        
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "current_directory": os.getcwd(),
            "timestamp": datetime.now().isoformat(),
            "environment": dict(list(os.environ.items())[:5])  # First 5 env vars
        }
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"System Information:\n{json.dumps(info, indent=2)}"
                )
            ]
        )
    
    elif name == "list_files":
        path = arguments.get("path", ".")
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Path does not exist: {path}")],
                    isError=True
                )
            
            if path_obj.is_file():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"{path} is a file, not a directory")]
                )
            
            files = []
            for item in path_obj.iterdir():
                files.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Contents of {path}:\n{json.dumps(files, indent=2)}"
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listing files: {str(e)}")],
                isError=True
            )
    
    elif name == "read_file":
        path = arguments.get("path")
        if not path:
            return CallToolResult(
                content=[TextContent(type="text", text="Path is required")],
                isError=True
            )
        
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"File does not exist: {path}")],
                    isError=True
                )
            
            with open(path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Contents of {path}:\n\n{content}"
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error reading file: {str(e)}")],
                isError=True
            )
    
    elif name == "write_demo_file":
        filename = arguments.get("filename")
        content = arguments.get("content", f"Demo file created at {datetime.now().isoformat()}")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Successfully wrote demo file: {filename}\nContent: {content}"
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error writing file: {str(e)}")],
                isError=True
            )
    
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
            isError=True
        )


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())