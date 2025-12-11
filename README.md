# Log MCP Server

An MCP server to read and search log files, with support for log rotation.

## Features

- **Read Logs**: Read the last N lines of a log file.
- **Tail Logs**: Read chunks of a log file from a specific offset.
- **Search Logs**: Search for text or regex patterns in log files.
- **Rotation Support**: Automatically handles rotated log files (e.g., `app.log`, `app.log.1`, `app.log.2`) when reading history.

## Installation

### From Source

1. Clone the repository.
2. Install dependencies (if any, e.g., `mcp`).
   ```bash
   pip install mcp
   ```

## Usage

### Running the Server

You can run the server directly using python:

```bash
# Add src to python path if needed, or install in editable mode
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python -m log_mcp_server
```

### Inspector

Use the MCP Inspector to test the server:

```bash
npx @modelcontextprotocol/inspector \
  python -m src.log_mcp_server
```

## Tools

- `read_log(path: str, lines: int = 100)`: Reads the last N lines.
- `read_log_chunk(path: str, offset: int, max_bytes: int = 4096)`: Reads a chunk from an offset.
- `search_log(path: str, pattern: str, is_regex: bool = False)`: Searches for patterns.