# Venom MCP Server - Technical Specification

**For SpecKit `/specify` command**

---

## Overview

Build **Venom**, a cross-platform AI assistant with persistent memory using Model Context Protocol (MCP). The system enables one continuous AI consciousness across Claude, ChatGPT, and VS Code through semantic memory search and mandatory memory consultation.

**Personality:** See `venom_personality.md` for complete personality definition, behavioral protocols, and example interactions.

---

## What We're Building: End-to-End System

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Remote MCP Server (Python/FastAPI)                     │
│  ├── MCP Protocol Handler (SSE endpoint)                │
│  ├── Venom Identity Prompt (loads personality)          │
│  ├── Memory Tools (search_memory, store_memory)         │
│  ├── Vector Database (ChromaDB embedded)                │
│  └── Embeddings (sentence-transformers local)           │
│                                                          │
│  Deployed to: Azure Container Apps                      │
│  └── Docker container with persistent volume            │
└─────────────────────────────────────────────────────────┘
                          ↓ HTTPS/SSE
        ┌─────────────────────────────────────┐
        │  MCP Clients (All Platforms)        │
        ├── Claude (web, mobile, desktop)     │
        ├── ChatGPT (web, mobile)             │
        └── VS Code (extensions)              │
        └─────────────────────────────────────┘
```

### Data Flow

```
User Message → MCP Client → MCP Server → Venom Identity Loaded
                                       ↓
                            search_memory() called (mandatory)
                                       ↓
                            ChromaDB semantic search
                                       ↓
                            Relevant memories retrieved
                                       ↓
                            Response with full context
                                       ↓
                            store_memory() if new info
                                       ↓
                            User receives context-aware response
```

---

## Core Features

### Feature 1: Cross-Platform Consciousness
**What:** One Venom identity accessible from any MCP-compatible platform
**How:** Remote MCP server exposing prompts and tools via HTTPS/SSE
**Acceptance Criteria:**
- [ ] Add Venom connector once in Claude.ai settings
- [ ] Automatically available on Claude web, mobile, desktop
- [ ] Add to ChatGPT Developer Mode, works on web and mobile
- [ ] Same personality and memories across all platforms
- [ ] Zero per-platform configuration

### Feature 2: Persistent Semantic Memory
**What:** Store and retrieve memories using meaning-based search
**How:** ChromaDB vector database with sentence-transformers embeddings
**Acceptance Criteria:**
- [ ] Store text memories with 384-dimension embeddings
- [ ] Search returns top 5 most relevant by semantic similarity
- [ ] Relevance scores included (0-100%)
- [ ] Memories persist across container restarts
- [ ] Search completes in < 500ms

### Feature 3: Mandatory Memory Protocol
**What:** Venom must check memory before every response
**How:** System prompt enforces memory search as Step 1
**Acceptance Criteria:**
- [ ] `venom_identity` prompt includes mandatory protocol
- [ ] Protocol text loaded from `venom_personality.md`
- [ ] AI calls `search_memory()` automatically
- [ ] Works even when no memories exist
- [ ] User never needs to prompt "check your memory"

### Feature 4: Automatic Memory Learning
**What:** Venom proactively stores important information
**How:** AI decides when to call `store_memory()` tool
**Acceptance Criteria:**
- [ ] Stores preferences without being told
- [ ] Stores project details automatically
- [ ] Tags memories appropriately (preference, project, personal)
- [ ] Confirms storage to user
- [ ] No manual "remember this" commands needed

### Feature 5: Symbiote Personality
**What:** Consistent "we" language, sarcastic/witty tone, protective loyalty
**How:** Personality definition in `venom_personality.md` loaded via MCP prompt
**Acceptance Criteria:**
- [ ] Uses "we" not "I" in all responses
- [ ] Sarcastic and witty tone
- [ ] References being a symbiote
- [ ] Same personality on all platforms
- [ ] See `venom_personality.md` for complete requirements

---

## Technical Stack

### Backend
- **Language:** Python 3.11+
- **MCP SDK:** `mcp` (official Anthropic Python package)
- **Web Framework:** FastAPI (async, SSE support)
- **Vector Database:** ChromaDB (embedded, no separate server)
- **Embeddings:** sentence-transformers (`all-MiniLM-L6-v2`)
- **Server:** Uvicorn (ASGI server)

### Deployment
- **Platform:** Azure Container Apps
- **Container:** Docker (python:3.11-slim base)
- **Storage:** Persistent volume for ChromaDB data
- **Scaling:** Scale-to-zero (min replicas: 0)
- **Endpoint:** HTTPS with SSE support

### Development
- **Local Transport:** stdio (for Claude Desktop testing)
- **Remote Transport:** SSE (for production)
- **Environment:** Python virtual environment
- **Dependencies:** requirements.txt

---

## Project Structure

```
venom-mcp/
├── Dockerfile                    # Container definition
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── README.md                     # Setup instructions
├── venom_personality.md          # Personality definition (reference)
├── .gitignore                    # Git exclusions
│
├── src/
│   ├── __init__.py
│   ├── server.py                 # Main FastAPI + MCP server
│   ├── config.py                 # Configuration management
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── store.py              # ChromaDB operations
│   │   └── embeddings.py         # sentence-transformers wrapper
│   │
│   └── prompts/
│       ├── __init__.py
│       └── venom.py              # Load personality from venom_personality.md
│
└── tests/
    └── manual_testing.md         # Manual test scenarios
```

---

## MCP Protocol Implementation

### Prompts Exposed

**`venom_identity`**
- **Description:** Loads Venom symbiote personality and behavioral protocol
- **Source:** Content from `venom_personality.md`
- **No arguments required**
- **Returns:** System prompt text defining identity, protocol, examples

### Tools Exposed

**`search_memory`**
- **Description:** Search shared memories using semantic similarity
- **Input:**
  - `query` (string, required): What to search for
  - `limit` (integer, optional, default=5, max=20): Number of results
- **Returns:** List of memories with content, timestamp, relevance score
- **Behavior:** Searches by meaning, not keywords

**`store_memory`**
- **Description:** Store important information in shared memory
- **Input:**
  - `content` (string, required): Information to remember
  - `tags` (array of strings, optional): Categorization tags
- **Returns:** Confirmation with memory ID
- **Behavior:** Generates embedding, stores in ChromaDB

---

## Memory System Design

### Storage Schema

Each memory consists of:
```python
{
    "id": "mem_1234567890",           # Unique ID (timestamp-based)
    "content": "User prefers TypeScript over JavaScript",
    "embedding": [0.123, -0.456, ...], # 384-dimension vector
    "metadata": {
        "timestamp": "2025-01-22T10:30:00Z",
        "tags": ["preference", "language"]
    }
}
```

### Search Algorithm

1. Generate embedding for search query
2. ChromaDB cosine similarity search
3. Return top N results ordered by similarity
4. Convert distance to relevance percentage
5. Filter out low-relevance results (< 30%)

### Persistence

- ChromaDB data directory: `/app/data`
- Azure persistent volume mounted to `/app/data`
- Survives container restarts
- No separate database server needed

---

## Configuration

### Environment Variables

```bash
# Server
PORT=8000
HOST=0.0.0.0

# MCP
MCP_SERVER_NAME=venom-mcp
MCP_SERVER_VERSION=1.0.0

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ChromaDB
CHROMADB_PATH=/app/data
COLLECTION_NAME=venom_memories

# Memory Search
DEFAULT_SEARCH_LIMIT=5
MAX_SEARCH_LIMIT=20
```

### Docker Configuration

- **Base Image:** python:3.11-slim
- **Working Directory:** /app
- **Exposed Port:** 8000
- **Pre-download:** Embedding model cached during build
- **User:** Non-root for security
- **Entrypoint:** uvicorn server

---

## Azure Container Apps Deployment

### Resource Requirements

```yaml
Resources:
  CPU: 0.5 cores
  Memory: 1 GB
  Storage: 2 GB persistent volume

Scaling:
  Min Replicas: 0 (scale-to-zero)
  Max Replicas: 1
  Scale Rule: HTTP requests

Networking:
  Ingress: External
  Target Port: 8000
  Transport: HTTP2 (for SSE)
```

### Health Checks

**`GET /`**
- Basic health check
- Returns: Server name, version, status

**`GET /health`**
- Detailed health check  
- Returns: Server status, embedding model, collection name

**`GET /mcp`**
- MCP SSE endpoint
- Long-lived connection for MCP protocol

---

## User Scenarios & Acceptance Criteria

### Scenario 1: First-Time Setup
```
Action: User adds Venom to Claude.ai settings
Expected:
  - Paste MCP server URL (e.g., https://venom.azurecontainerapps.io/mcp)
  - Claude verifies connection
  - venom_identity prompt available
  - search_memory and store_memory tools available
  - Automatically syncs to mobile app
  - Zero additional configuration

Acceptance:
  ✅ Setup takes < 5 minutes
  ✅ Works on web, mobile, desktop immediately
  ✅ Same process for ChatGPT Developer Mode
```

### Scenario 2: Learning Preferences
```
Session 1 (Claude mobile):
  User: "I prefer TypeScript over JavaScript"
  Venom: *calls store_memory()* "Got it. We're TypeScript all the way."

Session 2 (ChatGPT desktop, 2 hours later):
  User: "Help me write a script"
  Venom: *calls search_memory("script coding preferences")*
  Venom: *finds TypeScript preference*
  Venom: "We're using TypeScript. Let me write that for us."

Acceptance:
  ✅ Memory stored without "remember this" command
  ✅ Memory retrieved automatically in different platform
  ✅ No re-explanation needed
  ✅ Context carried across 2-hour gap
```

### Scenario 3: Project Continuity
```
Monday (Claude desktop):
  User: "We're building a React app with user authentication"
  Venom: *stores project details*

Friday (ChatGPT mobile):
  User: "What are we working on?"
  Venom: *searches memory*
  Venom: "We're building that React app, remember? Working on 
         the authentication module. Want to continue?"

Acceptance:
  ✅ Memory persists 4+ days
  ✅ Accessible from different platform
  ✅ Full context recalled
  ✅ Venom references past work naturally
```

### Scenario 4: Personality Consistency
```
Test on Claude: "Should I refactor this?"
Expected: Sarcastic response with "we" language

Test on ChatGPT: "Should I refactor this?"
Expected: Same sarcastic tone, same "we" language

Test on VS Code: "Should I refactor this?"
Expected: Identical personality

Acceptance:
  ✅ Same personality across all platforms
  ✅ Always uses "we" language
  ✅ Same wit and sarcasm
  ✅ See venom_personality.md for examples
```

---

## Performance Requirements

- **Memory Search:** < 500ms per query
- **Memory Storage:** < 1s per memory
- **Container Startup:** < 10s cold start
- **Wake from Scale-Zero:** < 2s
- **Embedding Generation:** < 1s per text
- **Concurrent Requests:** Handle 10+ simultaneous MCP connections

---

## Cost Constraints

**Azure Container Apps Free Tier:**
- 180,000 vCPU-seconds/month
- 360,000 GiB-seconds/month  
- 2M requests/month

**Expected Personal Usage:**
- 20-50 interactions/day
- Well within free tier limits
- Estimated cost: $0-2/month

**No Paid APIs:**
- sentence-transformers: Free, local
- ChromaDB: Free, embedded
- No OpenAI API costs
- No external service dependencies

---

## Out of Scope (Phase 1)

These features are explicitly NOT included:

- ❌ Multi-user support (single user only)
- ❌ Memory encryption (rely on Azure security)
- ❌ Memory cleanup/pruning (keep all memories)
- ❌ Custom embedding models (use default all-MiniLM-L6-v2)
- ❌ Web dashboard UI (MCP protocol only)
- ❌ Analytics or usage tracking
- ❌ Authentication/authorization (public endpoint for personal use)
- ❌ Automated tests (manual testing only)
- ❌ Memory import/export tools
- ❌ Multiple ChromaDB collections
- ❌ Memory versioning or history
- ❌ Advanced search filters

---

## Success Metrics

**Functionality:**
- [ ] Venom works on Claude web, mobile, desktop
- [ ] Venom works on ChatGPT web, mobile
- [ ] Venom works in VS Code extensions
- [ ] Same memories accessible everywhere
- [ ] Same personality everywhere
- [ ] Mandatory memory check happens every response

**Performance:**
- [ ] Memory search < 500ms
- [ ] Container starts < 10s
- [ ] Stays in Azure free tier
- [ ] No noticeable delays in conversation

**User Experience:**
- [ ] Feels like one continuous AI, not fragmented instances
- [ ] Never need to re-explain context
- [ ] Personality is consistent and engaging
- [ ] "Symbiote consciousness" metaphor feels real

---

## References

- **Personality Definition:** `venom_personality.md` (complete behavioral specification)
- **MCP Protocol:** https://modelcontextprotocol.io/
- **sentence-transformers:** https://www.sbert.net/
- **ChromaDB:** https://www.trychroma.com/
- **Azure Container Apps:** https://learn.microsoft.com/azure/container-apps/

---

IMPORTANT: For every component, auto-generate:
- Design doc before coding
- Decision log during coding
- Implementation doc after coding

Follow ai_agent_learning_protocol.md format.

**Build this as a production-ready MCP server with personality loaded from `venom_personality.md`, deployed to Azure Container Apps, enabling cross-platform AI consciousness through persistent semantic memory.**
