# MCP Server Demo

This directory contains a simple MCP (Model Context Protocol) server demonstration.

## Files

- `mcp_demo_server.py` - Main MCP server implementation
- `mcp_config.json` - Configuration file for MCP client
- `test_mcp_server.py` - Test script for the server
- `MCP_DEMO_README.md` - This documentation file

## Features

The demo MCP server provides the following tools:

1. **get_system_info** - Returns basic system information
2. **list_files** - Lists files in a specified directory
3. **read_file** - Reads the contents of a file
4. **write_demo_file** - Creates a demo file with timestamp

## Usage

### Running the Server

```bash
python3 mcp_demo_server.py
```

### Testing the Server

```bash
python3 test_mcp_server.py
```

### Configuration

The `mcp_config.json` file can be used to configure MCP clients to connect to this server:

```json
{
  "mcpServers": {
    "demo-server": {
      "command": "python3",
      "args": ["mcp_demo_server.py"],
      "env": {}
    }
  }
}
```

## Integration with Claude Code

To use this MCP server with Claude Code, you can:

1. Add the server configuration to your MCP client settings
2. The server will provide file system tools that extend Claude's capabilities
3. Tools can be used for reading, writing, and exploring files in your project

## Requirements

- Python 3.10+
- `mcp` package (installed via `pip install mcp`)

## Security Note

This is a demo server intended for learning purposes. In production environments, ensure proper security measures are implemented for file system access.