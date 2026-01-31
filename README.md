# Venom MCP Server

Cross-platform AI consciousness through persistent semantic memory.

## Overview

Venom is a remote MCP (Model Context Protocol) server that provides:
- **Persistent semantic memory** across all your AI platforms (Claude, ChatGPT, etc.)
- **Cross-platform consciousness** - same memories accessible from web, mobile, desktop
- **Venom symbiote personality** - enforcing "we" language and mandatory memory checks
- **Free tier deployment** - runs on Azure Container Apps with scale-to-zero

## Quick Start

### Local Development

1. **Clone and setup**:
   ```bash
   git clone https://github.com/yourusername/symbiote-mcp.git
   cd symbiote-mcp

   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults work for local development)
   ```

3. **Run the server**:
   ```bash
   # For Claude Desktop (stdio transport)
   python -m src.server --stdio

   # For remote clients (SSE transport)
   python -m src.server
   ```

4. **Test the server**:
   ```bash
   curl http://localhost:8000/health
   ```

### Docker

1. **Build the image**:
   ```bash
   docker build -t venom-mcp:latest .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 -v $(pwd)/data:/app/data venom-mcp:latest
   ```

### Claude Desktop Integration

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on Mac):

```json
{
  "mcpServers": {
    "venom": {
      "command": "python",
      "args": ["/absolute/path/to/symbiote-mcp/src/server.py", "--stdio"],
      "env": {
        "CHROMADB_PATH": "/absolute/path/to/symbiote-mcp/data"
      }
    }
  }
}
```

Restart Claude Desktop after configuration.

## Personality Variants

Venom supports multiple personality variants for experimentation:

```bash
# Use default personality
VENOM_PERSONALITY=default python -m src.server

# Use alternative personality
VENOM_PERSONALITY=variant2 python -m src.server
```

Check which variant is active:
```bash
curl http://localhost:8000/health | jq '.personality_variant'
```

## Features

- **Semantic Memory**: Store and search memories using meaning, not keywords
- **Vector Embeddings**: sentence-transformers with 384-dimension vectors
- **Persistent Storage**: ChromaDB with file-based persistence
- **MCP Protocol**: Remote server via SSE, supports stdio for local use
- **Free Deployment**: Azure Container Apps with scale-to-zero
- **Personality System**: Load personality from markdown files

## MCP Tools

### search_memory
Search shared memories using semantic similarity.

**Parameters**:
- `query` (string, required): Natural language search query
- `limit` (integer, optional): Maximum results (1-20, default: 5)

**Returns**: Array of memories with relevance scores

### store_memory
Store important information in shared memory.

**Parameters**:
- `content` (string, required): Information to remember
- `tags` (array, optional): Categorization tags (max 10)

**Returns**: Memory ID, timestamp, and success status

## Architecture

```
src/
├── server.py           # FastAPI + MCP server
├── config.py           # Configuration management
├── memory/
│   ├── embeddings.py   # sentence-transformers wrapper
│   └── store.py        # ChromaDB operations
└── prompts/
    └── venom.py        # Personality loader
```

## Requirements

- Python 3.11+
- 1GB RAM minimum
- Docker (for deployment)
- Azure account (for production deployment)

## Documentation

- **Specification**: [specs/001-venom-mcp-server/spec.md](specs/001-venom-mcp-server/spec.md)
- **Implementation Plan**: [specs/001-venom-mcp-server/plan.md](specs/001-venom-mcp-server/plan.md)
- **Quickstart Guide**: [specs/001-venom-mcp-server/quickstart.md](specs/001-venom-mcp-server/quickstart.md)
- **Data Model**: [specs/001-venom-mcp-server/data-model.md](specs/001-venom-mcp-server/data-model.md)
- **API Contracts**: [specs/001-venom-mcp-server/contracts/mcp-schema.json](specs/001-venom-mcp-server/contracts/mcp-schema.json)

## License

MIT
