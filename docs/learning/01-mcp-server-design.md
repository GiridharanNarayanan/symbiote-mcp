# MCP Server - Design

## What We're Building

A FastAPI-based web server that implements the Model Context Protocol (MCP), allowing AI assistants to access Venom's personality and memory tools. The server supports two transports: SSE (Server-Sent Events) for remote clients like Claude Web/Mobile, and stdio (standard input/output) for local clients like Claude Desktop.

**Location in architecture:** `src/server.py` (main entry point, orchestrates all other components)

**Dependencies:** FastAPI, uvicorn, mcp SDK, config, memory system, prompts system

**Used by:** AI clients (Claude Desktop, Claude Web, ChatGPT, etc.)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      AI Clients                              │
│   (Claude Desktop, Claude Web, ChatGPT with MCP plugin)     │
└────────────┬──────────────────────────┬─────────────────────┘
             │                          │
        stdio (local)            SSE over HTTP (remote)
             │                          │
             ↓                          ↓
┌────────────────────────────────────────────────────────────┐
│                    src/server.py                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI Application                                 │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐ │  │
│  │  │ / (root)   │  │ /health    │  │ /mcp (SSE)     │ │  │
│  │  │ endpoint   │  │ endpoint   │  │ endpoint       │ │  │
│  │  └────────────┘  └────────────┘  └────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MCP Server Instance                                 │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │ list_prompts │  │ get_prompt   │  │ list_tools │ │  │
│  │  │ handler      │  │ handler      │  │ handler    │ │  │
│  │  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │  │
│  │         │                  │                 │        │  │
│  │         ↓                  ↓                 ↓        │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │ call_tool handler                               │ │  │
│  │  │ - search_memory                                 │ │  │
│  │  │ - store_memory                                  │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Global Service Instances (initialized at startup)  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │ VenomPrompt  │  │MemoryStore   │  │Config      │ │  │
│  │  │              │  │              │  │            │ │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

## Why This Design?

### Technology Choice: FastAPI + MCP SDK

**Alternatives Considered:**

1. **Flask with custom MCP implementation**
   - **Pros:** Lighter weight, more control over implementation
   - **Cons:** No native async support, would need to write SSE handling, no type validation
   - **Why rejected:** FastAPI's async/await is critical for performance, type hints improve code quality

2. **Pure ASGI (no framework)**
   - **Pros:** Maximum performance, minimal overhead
   - **Cons:** Too low-level, would need to implement routing, request parsing, response handling
   - **Why rejected:** Reinventing the wheel, violates "simplicity" principle

3. **Django**
   - **Pros:** Batteries included, ORM, admin panel
   - **Cons:** Heavy framework, overkill for API-only server, slower startup
   - **Why rejected:** We don't need ORM or templates, just API endpoints

4. **aiohttp**
   - **Pros:** Pure async framework, good for websockets
   - **Cons:** Less intuitive than FastAPI, no automatic API docs, weaker ecosystem
   - **Why rejected:** FastAPI provides better developer experience with similar performance

**Why We Chose FastAPI + Official MCP SDK:**

1. **Native async/await**: Required by constitution, critical for handling concurrent requests efficiently
2. **Type hints integration**: Pydantic validation catches errors at request time, improves code quality
3. **Built-in SSE support**: EventSourceResponse makes Server-Sent Events trivial
4. **Official MCP SDK**: Ensures protocol compliance, handles serialization/deserialization
5. **Fast development**: Automatic API docs, dependency injection, minimal boilerplate
6. **Production ready**: Widely used, well-maintained, excellent performance

### Key Concepts

#### Concept 1: MCP (Model Context Protocol)

**Simple Explanation:**
MCP is like a universal adapter for AI assistants. Instead of each AI platform (Claude, ChatGPT, etc.) having its own custom API, MCP provides one standard way for AI assistants to:
- Get prompts (like personality definitions)
- Call tools (like search_memory, store_memory)
- Share data across platforms

Think of it like USB-C: one connector that works with everything.

**Why It Matters:**
Without MCP:
- Claude Web needs its own API
- Claude Desktop needs a different integration
- ChatGPT needs yet another implementation
- No shared memory across platforms ❌

With MCP:
- Write the server once
- All MCP clients can connect
- Same tools and prompts everywhere
- Shared memory across all platforms ✅

**Learn More:**
- MCP Protocol Spec: https://modelcontextprotocol.io/
- MCP Python SDK: https://github.com/anthropics/mcp-python

#### Concept 2: Server-Sent Events (SSE)

**Simple Explanation:**
SSE is a way for servers to send updates to clients over HTTP. Unlike regular HTTP where the client asks once and gets one response, SSE keeps the connection open so the server can send multiple messages.

```
Regular HTTP:
Client: "What's the time?"
Server: "3:00 PM"
[connection closes]

SSE:
Client: "Keep me updated on the time"
Server: "3:00 PM"
Server: "3:01 PM"
Server: "3:02 PM"
[connection stays open]
```

**Why It Matters:**
MCP needs bi-directional communication:
- Client sends: "Call search_memory tool"
- Server sends: "Processing..."
- Server sends: "Here are the results"
- Client sends: "Call store_memory tool"
- ...and so on

SSE allows this continuous conversation without opening new connections each time.

**Learn More:**
- SSE Specification: https://html.spec.whatwg.org/multipage/server-sent-events.html
- FastAPI SSE: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse

#### Concept 3: stdio (Standard Input/Output)

**Simple Explanation:**
stdio is how programs communicate through the command line:
- **stdin**: Read input (like typing into the program)
- **stdout**: Write output (what the program prints)

Instead of HTTP, MCP can run over stdio for local programs.

```
# Over HTTP (remote)
curl http://server.com/mcp → Response

# Over stdio (local)
echo "MCP request" | ./server.py → Response printed to screen
```

**Why It Matters:**
Claude Desktop runs on your computer. Instead of making HTTP requests to localhost (overhead, port conflicts), it can:
1. Launch `python server.py --stdio` as a subprocess
2. Send MCP requests through stdin
3. Receive responses through stdout

Faster, simpler, no network involved.

**Learn More:**
- stdin/stdout basics: https://en.wikipedia.org/wiki/Standard_streams
- MCP stdio transport: https://modelcontextprotocol.io/docs/transports/stdio

#### Concept 4: Async/Await in Python

**Simple Explanation:**
Normally, Python code runs one line at a time:
```python
result1 = slow_function()  # Waits 5 seconds
result2 = another_function()  # Waits 3 seconds
# Total: 8 seconds
```

With async/await, Python can work on other things while waiting:
```python
result1 = await slow_function()  # Start waiting (5s), but handle other requests
result2 = await another_function()  # Handle more requests during this 3s
# Server stays responsive during waits
```

**Why It Matters:**
- Embedding generation: ~500ms
- ChromaDB search: ~200ms
- If we block, server can only handle 1 request every 700ms
- With async, server can handle 10+ concurrent requests

**Learn More:**
- Python async tutorial: https://realpython.com/async-io-python/
- FastAPI async guide: https://fastapi.tiangolo.com/async/

#### Concept 5: Lifespan Events

**Simple Explanation:**
Lifespan events are special functions that run when the server starts/stops:

```python
@asynccontextmanager
async def lifespan(app):
    # Startup code (runs once when server starts)
    print("Loading model...")
    model = load_embedding_model()  # 2-3 seconds

    yield  # Server runs here (handles requests)

    # Shutdown code (runs when server stops)
    print("Cleaning up...")
```

**Why It Matters:**
Loading the 80MB embedding model takes 2-3 seconds. We want to do this ONCE when the server starts, not on every request.

Without lifespan:
- First request: Load model (3s) + generate embedding (0.5s) = 3.5s ❌

With lifespan:
- Startup: Load model once (3s)
- All requests: Generate embedding (0.5s) ✅

**Learn More:**
- FastAPI lifespan: https://fastapi.tiangolo.com/advanced/events/

## How It Works

### Input

**SSE Transport (Remote):**
```http
GET /mcp HTTP/1.1
Host: venom-mcp.azurecontainerapps.io
Accept: text/event-stream
```

**stdio Transport (Local):**
```bash
python -m src.server --stdio
# Server reads from stdin, writes to stdout
```

### Process

**Step 1: Server Initialization (Lifespan Startup)**
1. Load environment variables from config
2. Initialize embedding service (load model into memory)
3. Initialize memory store (connect to ChromaDB)
4. Load Venom personality from file
5. Create MCP server instance
6. Register MCP handlers (prompts, tools)

**Step 2: Client Connection**
- **SSE**: Client makes GET request to `/mcp`, connection stays open
- **stdio**: Client launches server as subprocess, communicates via pipes

**Step 3: MCP Request Handling**

When client sends request:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {}
}
```

Server flow:
1. MCP SDK deserializes JSON
2. Calls registered handler (`list_tools()`)
3. Handler returns tool definitions
4. MCP SDK serializes to JSON
5. Sends response to client

**Step 4: Tool Execution**

When client calls tool:
```json
{
  "method": "tools/call",
  "params": {
    "name": "search_memory",
    "arguments": {"query": "coding preferences", "limit": 5}
  }
}
```

Server flow:
1. MCP SDK routes to `call_tool()` handler
2. Handler checks tool name
3. Calls `memory_store.search_memory(query, limit)`
4. Memory store generates embedding, searches ChromaDB
5. Results formatted and returned to client

### Output

**MCP Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "results": [
      {
        "memory_id": "mem_1706745600",
        "content": "User prefers TypeScript",
        "relevance_score": 87.5
      }
    ]
  }
}
```

## Edge Cases

| Scenario | How We Handle It | Why This Works |
|----------|------------------|----------------|
| **Server starts without ChromaDB directory** | Create directory automatically in memory_store init | Better UX than failing, mkdir is safe operation |
| **Embedding model not downloaded** | Download on first startup (takes 30s-1min) | Only happens once, model cached locally after |
| **Client disconnects mid-request** | FastAPI handles connection errors gracefully | No memory leaks, resources cleaned up |
| **Multiple concurrent requests** | async/await handles concurrency | Each request gets its own context, no blocking |
| **Invalid tool name** | Raise ValueError, return error to client | Clear error message helps debugging |
| **stdio mode without --stdio flag** | Run uvicorn server instead | Defaults to HTTP/SSE transport |
| **Port already in use** | Uvicorn fails with clear error | Better to fail fast than silently bind wrong port |
| **Personality file not found** | Raise FileNotFoundError on startup | Fail fast, better than serving broken prompts |

## What You'll Learn

After implementing this component, you should understand:

- [ ] What MCP is and why it's useful for cross-platform AI tools
- [ ] How Server-Sent Events enable streaming communication
- [ ] The difference between HTTP and stdio transports
- [ ] Why async/await improves web server performance
- [ ] How FastAPI's dependency injection works
- [ ] How to structure a production-ready Python web server
- [ ] The role of lifespan events in server initialization
- [ ] How MCP handlers are registered and called

## Design Decisions Summary

**Key Decision 1: FastAPI instead of Flask**
- **Trade-off**: Slightly newer (less mature ecosystem), but better async support
- **Why it's worth it**: async/await is critical for performance, type hints improve reliability

**Key Decision 2: Support both SSE and stdio transports**
- **Trade-off**: More code complexity (two transport implementations)
- **Why it's worth it**: SSE for cloud deployment, stdio for local Claude Desktop

**Key Decision 3: Use lifespan events for model pre-loading**
- **Trade-off**: Slower server startup (3-5 seconds), but much faster requests
- **Why it's worth it**: Startup happens once, requests happen thousands of times

**Key Decision 4: Global service instances instead of dependency injection**
- **Trade-off**: Harder to test (global state), but simpler code
- **Why it's worth it**: Single-user server, testing not critical in Phase 1

**Key Decision 5: Duplicate MCP handler registration for stdio and SSE**
- **Trade-off**: Code duplication between `app.py` (SSE) and `run_stdio()` (stdio)
- **Why it's worth it**: Keeps each transport self-contained, easier to understand

## Going Deeper

**Next steps to extend your understanding:**

1. **Read MCP specification**: Understand protocol details, message format, error handling
2. **Explore FastAPI advanced features**: Middleware, background tasks, websockets
3. **Study async patterns**: asyncio, event loops, coroutines, concurrent execution
4. **Compare transports**: When to use SSE vs WebSockets vs HTTP polling

**Resources:**

- **MCP Protocol**: https://modelcontextprotocol.io/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Python asyncio**: https://docs.python.org/3/library/asyncio.html
- **Server-Sent Events**: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events

**Optional improvements to consider:**

1. **Add authentication**: API keys or JWT tokens for production
2. **Rate limiting**: Prevent abuse from external clients
3. **Metrics/logging**: Prometheus metrics, structured logging
4. **WebSocket transport**: Alternative to SSE for bidirectional communication
5. **CORS configuration**: Allow web clients from specific domains
