# Venom MCP Server - Learning Overview

## Project Architecture

This is a remote MCP (Model Context Protocol) server that provides cross-platform AI consciousness through persistent semantic memory.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  AI Clients (Claude Desktop, Claude Web, ChatGPT, etc.)    │
└────────────────┬────────────────────────────────────────────┘
                 │ MCP Protocol (SSE or stdio)
                 ↓
┌─────────────────────────────────────────────────────────────┐
│           Venom MCP Server (FastAPI + MCP SDK)              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Prompts    │  │  Memory      │  │  Configuration   │   │
│  │  System     │  │  System      │  │  Management      │   │
│  │             │  │              │  │                  │   │
│  │  venom.py   │  │  store.py    │  │  config.py       │   │
│  │             │  │  embeddings.py│  │                 │   │
│  └─────────────┘  └──────┬───────┘  └──────────────────┘   │
│                           │                                  │
│                           ↓                                  │
│                  ┌────────────────┐                          │
│                  │   ChromaDB     │                          │
│                  │   (embedded)   │                          │
│                  └────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓ persists to
                    ┌──────────────┐
                    │  /app/data   │ (persistent volume)
                    └──────────────┘
```

### Core Components

1. **MCP Server** (`src/server.py`)
   - FastAPI web framework
   - MCP protocol implementation (prompts + tools)
   - SSE transport for remote clients
   - stdio transport for local clients

2. **Embedding System** (`src/memory/embeddings.py`)
   - sentence-transformers library
   - all-MiniLM-L6-v2 model (384 dimensions)
   - Converts text to semantic vectors

3. **Memory Store** (`src/memory/store.py`)
   - ChromaDB vector database (embedded mode)
   - Semantic search using cosine similarity
   - Persistent file-based storage

4. **Prompts System** (`src/prompts/venom.py`)
   - Loads Venom personality from markdown file
   - Exposes as MCP prompt
   - Supports multiple personality variants

5. **Configuration** (`src/config.py`)
   - Environment variable management
   - Validation and defaults
   - Personality variant selection

### Data Flow

#### Storing a Memory

```
User: "I prefer TypeScript for all projects"
     ↓
AI Client calls store_memory tool
     ↓
MCP Server receives tool call
     ↓
Generate embedding: [0.234, -0.567, ..., 0.089] (384 numbers)
     ↓
Store in ChromaDB:
  - ID: mem_1706745600
  - Content: "I prefer TypeScript for all projects"
  - Embedding: [0.234, -0.567, ..., 0.089]
  - Metadata: {timestamp, tags}
     ↓
Persist to disk: /app/data/chroma.sqlite3
     ↓
Return: {memory_id: "mem_1706745600", success: true}
```

#### Searching Memory

```
User: "What languages do I like?"
     ↓
AI Client calls search_memory tool
     ↓
MCP Server receives tool call
     ↓
Generate query embedding: [0.198, -0.523, ..., 0.102]
     ↓
ChromaDB cosine similarity search:
  - Compare query embedding to all stored embeddings
  - Find closest matches
  - Calculate relevance scores
     ↓
Filter results (relevance >= 30%)
     ↓
Return top N results with scores:
  [
    {
      memory_id: "mem_1706745600",
      content: "I prefer TypeScript for all projects",
      relevance_score: 87.5,
      ...
    }
  ]
```

### Key Technologies

| Technology | Purpose | Why This Choice |
|-----------|---------|-----------------|
| **Python 3.11+** | Programming language | Modern async/await, type hints, AI/ML ecosystem |
| **FastAPI** | Web framework | Native async, SSE support, type validation |
| **mcp** | MCP protocol | Official SDK ensures spec compliance |
| **sentence-transformers** | Embeddings | Free, local, good quality (384-dim vectors) |
| **ChromaDB** | Vector database | Embedded mode, no separate server, persistent |
| **Uvicorn** | ASGI server | Fast, HTTP/2 support for SSE |
| **Docker** | Containerization | Consistent deployment, pre-download model |
| **Azure Container Apps** | Hosting | Scale-to-zero, free tier, persistent volumes |

### Learning Path

**Recommended reading order:**

1. **Start here**: [01-mcp-server-design.md](./01-mcp-server-design.md) - Understand MCP protocol
2. **Then**: [02-embeddings-design.md](./02-embeddings-design.md) - Learn about vector embeddings
3. **Next**: [03-chromadb-design.md](./03-chromadb-design.md) - Understand vector databases
4. **Follow with**: [04-mcp-prompts-design.md](./04-mcp-prompts-design.md) - Personality system
5. **Finally**: [05-docker-design.md](./05-docker-design.md) - Containerization concepts

After reading design docs, review the corresponding implementation docs to see how theory translates to code.

### Key Concepts

#### Semantic Search
Instead of keyword matching, semantic search finds results based on **meaning**. "What languages do I like?" will match "I prefer TypeScript" even though they share no words.

#### Vector Embeddings
Text converted to lists of numbers (vectors) where similar meanings have similar numbers. Think of it like GPS coordinates - similar words are "close together" in this 384-dimensional space.

#### MCP Protocol
A standardized way for AI assistants to access tools and prompts. Instead of each AI platform having its own API, MCP provides one protocol that works everywhere.

#### Scale-to-Zero
Container automatically shuts down when not in use (costs $0), then wakes up in <2 seconds when needed. Perfect for personal projects with intermittent usage.

### Project Goals

1. **Cross-platform memory**: Same memories accessible from any AI platform
2. **Free to run**: No ongoing costs (Azure free tier)
3. **Educational value**: Learn MCP, vectors, embeddings, Docker, Azure
4. **Simple architecture**: Minimal abstractions, clear separation of concerns
5. **Personality consistency**: Venom persona enforced across all platforms

### Success Metrics

- ✅ Memory persists across sessions
- ✅ Search returns relevant results (not just keyword matches)
- ✅ Server responds in <500ms for typical queries
- ✅ Container scales to zero when idle
- ✅ Total cost stays at $0/month
- ✅ Same personality across all clients

### Next Steps

After reviewing this overview:
1. Read component design docs to understand architectural decisions
2. Review implementation docs to see how concepts translate to code
3. Try manual testing scenarios to verify behavior
4. Experiment with personality variants
5. Deploy to Azure Container Apps for cross-platform access

### Glossary Quick Reference

See [99-glossary.md](./99-glossary.md) for detailed definitions of all terms used in this project.
