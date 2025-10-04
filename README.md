# Agent-Ethan2 Guide MCP Server

[日本語](./README.ja.md)

An MCP server that provides agent-ethan2 framework documentation and source code to coding agents, helping them implement using the framework.

## Features

- 🚀 **Easy Setup**: No installation required via uvx, just configure and start
- 📦 **Auto Download**: Automatically fetches specified version of agent-ethan2 from GitHub
- 📝 **Auto Configuration**: Automatically writes documentation and source code location to AGENTS.md
- 🔄 **Version Management**: Easy version switching

## Quick Start

### 1. MCP Client Configuration

Add the following to your MCP client configuration (Cursor, Claude Desktop, Cline, etc.):

**For Cursor** (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "agent-ethan-guide": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/eijifuku/agent-ethan-guide-mcp",
        "agent-ethan-guide-mcp"
      ],
      "env": {
        "SETUP_RULEFILE": "AGENTS.md",
        "SETUP_TMP_DIR": "./tmp"
      }
    }
  }
}
```

**For Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

Use the same JSON format.

**Note**: 
- It's recommended to use **absolute paths** for `SETUP_RULEFILE` and `SETUP_TMP_DIR`
- Specify a directory outside your repository or a directory listed in `.gitignore` for `SETUP_TMP_DIR`

```json
"env": {
  "SETUP_RULEFILE": "/path/to/your/project/AGENTS.md",
  "SETUP_TMP_DIR": "/path/to/your/project/tmp"  // Add to .gitignore
}
```

`.gitignore` example:
```
tmp/
AGENTS.md
```

### 2. Restart Client

Restart your MCP client to apply the configuration.

### 3. Run setup tool

Execute setup tool via MCP client:

```
setup(version="v0.1.1")
```

This will:
- Download agent-ethan2 v0.1.1 from GitHub
- Extract to specified directory
- Write location to AGENTS.md

### 4. Done!

agent-ethan2 documentation and source code are now available. When you ask agents questions, they will automatically reference AGENTS.md and use agent-ethan2 information.

## setup Tool

### Parameters

- `version` (required): agent-ethan2 GitHub tag (e.g., "v0.1.1", "v0.1.0")

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SETUP_RULEFILE` | `AGENTS.md` | Path to rule file |
| `SETUP_TMP_DIR` | `./tmp` | Download directory |

**Important**: When using relative paths, they are interpreted relative to the MCP client's startup directory. If you want to create files in different locations per project, specify absolute paths.

### Available Versions

Check available versions on [GitHub releases page](https://github.com/eijifuku/agent-ethan2/tags).

### Examples

```
# Setup latest version
setup(version="v0.1.1")

# Setup specific version
setup(version="v0.1.0")
```

### Changing Versions

To switch to a new version:

1. Delete old directory (or leave it)
2. Run setup with new version

```bash
# Delete old version (optional)
rm -rf ./tmp/agent-ethan2-0.1.0

# Setup new version
setup(version="v0.1.1")
```

AGENTS.md will be automatically updated.

## For Developers

### Local Development & Testing

#### Prerequisites

- Python 3.10 or later
- Docker & Docker Compose (for Docker method)
- uv (for uvx method)

#### uvx Method (Recommended)

```bash
# Clone repository
git clone https://github.com/eijifuku/agent-ethan-guide-mcp.git
cd agent-ethan-guide-mcp

# Run from local
uvx --from . agent-ethan-guide-mcp
```

#### Docker Method

For testing in HTTP mode:

```bash
# Change configs/server.yaml to HTTP mode
# run_options:
#   transport: http
#   host: 0.0.0.0
#   port: 8009
#   path: /mcp

# Start container
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Running Tests

```bash
# Install dependencies
pip install -e .[dev]

# Run tests
pytest tests/
```

### Project Structure

```
agent-ethan-guide-mcp/
├── mcp_app/
│   └── tools/
│       └── agent_ethan_setup.py  # setup tool implementation
├── mcp_server.py                 # MCP server entry point
├── configs/
│   └── server.yaml              # Server configuration
├── tests/                       # Test code
├── pyproject.toml              # Package configuration
└── README.md                   # This file
```

## Troubleshooting

### setup tool not found

Restart your MCP client and check the MCP server connection status.

### Files not created in expected location

Specify absolute paths in environment variables:

```json
"env": {
  "SETUP_RULEFILE": "/home/user/projects/myproject/AGENTS.md",
  "SETUP_TMP_DIR": "/home/user/projects/myproject/tmp"
}
```

### Version not found (HTTP 404)

Check if the specified version tag exists in the agent-ethan2 repository.

Available versions: https://github.com/eijifuku/agent-ethan2/tags

## License

See the LICENSE file for license information.

## Related Links

- [agent-ethan2](https://github.com/eijifuku/agent-ethan2) - AI Agent Framework
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP Server Framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP Specification
