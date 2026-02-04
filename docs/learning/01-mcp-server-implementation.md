# MCP Server - Implementation Walkthrough

## Code Overview

**File:** `src/server.py`
**Lines of Code:** ~350
**External Dependencies:** fastapi, uvicorn, mcp, dotenv
**Internal Dependencies:** config, memory (embeddings, store), prompts (venom)

## Key Code Sections

### Section 1: Imports and Global State

```python
from fastapi import FastAPI
from mcp import types
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server

# Global instances (initialized in lifespan)
embedding_service: EmbeddingService | None = None
memory_store: MemoryStore | None = None
venom_prompt: VenomPrompt | None = None
mcp_server: Server | None = None
```

**What This Does:**
Sets up global variables to hold service instances that will be initialized once and reused across all requests.

**Line-by-Line:**
- `from mcp import types`: MCP protocol type definitions (Prompt, Tool, TextContent, etc.)
- `from mcp.server import Server`: Main MCP server class
- `from mcp.server.sse import SseServerTransport`: Server-Sent Events transport
- `from mcp.server.stdio import stdio_server`: Standard input/output transport
- Global variables with `| None` type hints: Start as None, populated during startup

**What Would Break:**
If we removed the global variables, we'd have to pass these services through every function call (dependency injection). That works but adds complexity. The globals are safe here because:
1. Single-user server (no multi-tenancy concerns)
2. Services are immutable after initialization
3. Only written during startup, read during requests

### Section 2: Lifespan Context Manager

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup/shutdown."""
    global embedding_service, memory_store, venom_prompt, mcp_server

    print("=" * 60)
    print("Venom MCP Server - Starting")
    print("=" * 60)

    # Initialize embedding service
    print(f"Initializing embedding service: {config.embedding_model}")
    embedding_service = EmbeddingService(model_name=config.embedding_model)

    # Initialize memory store
    print(f"Initializing memory store: {config.chromadb_path}")
    memory_store = MemoryStore(
        chromadb_path=config.chromadb_path,
        collection_name=config.collection_name,
        embedding_service=embedding_service,
    )

    # Initialize Venom personality prompt
    personality_path = config.get_personality_file_path()
    print(f"Loading personality variant: {config.venom_personality}")
    venom_prompt = VenomPrompt(personality_file_path=personality_path)

    # Initialize MCP server
    mcp_server = Server("venom-mcp")

    # Register MCP handlers (shown in next section)
    # ...

    print("=" * 60)
    print(f"Server ready on http://{config.host}:{config.port}")
    print("=" * 60)

    yield

    # Shutdown
    print("Shutting down Venom MCP Server...")
```

**What This Does:**
Runs once when FastAPI starts, initializes all expensive resources (model loading, database connection), then yields control to the running server. On shutdown, runs cleanup code.

**Line-by-Line:**
- `@asynccontextmanager`: Decorator that creates an async context manager (enables `async with`)
- `global embedding_service, ...`: Declare we're modifying global variables
- Initialization order matters:
  1. Embedding service first (no dependencies)
  2. Memory store second (depends on embedding service)
  3. Venom prompt third (depends on config)
  4. MCP server last (depends on all services)
- `yield`: Pauses here, server runs, resumes on shutdown
- Code after `yield`: Runs when server stops (Ctrl+C, container restart, etc.)

**What Would Break:**
If we removed this and initialized services in route handlers:
- Every request would reload the 80MB model (3 seconds each) ❌
- Memory usage would spike from re-creating ChromaDB connections
- First request would be very slow, subsequent requests also slow

With lifespan:
- Startup: 3-5 seconds once
- All requests: Fast (<1s) ✅

### Section 3: MCP Prompt Handlers

```python
@mcp_server.list_prompts()
async def list_prompts() -> List[types.Prompt]:
    """List available prompts."""
    return [
        types.Prompt(
            name="venom_identity",
            description="Venom symbiote personality with mandatory memory protocol",
        )
    ]

@mcp_server.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str] | None = None) -> types.GetPromptResult:
    """Get a specific prompt by name."""
    if name != "venom_identity":
        raise ValueError(f"Unknown prompt: {name}")

    prompt_data = venom_prompt.get_prompt()

    return types.GetPromptResult(
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=prompt_data["content"],
                ),
            )
        ]
    )
```

**What This Does:**
Registers handlers for MCP prompt requests. When a client asks "what prompts are available?", it gets `venom_identity`. When it requests that prompt, it gets the personality content from the file.

**Line-by-Line:**
- `@mcp_server.list_prompts()`: Decorator registers this function as the handler for "prompts/list" MCP method
- `return [types.Prompt(...)]`: Return list of available prompts (we only have one)
- `@mcp_server.get_prompt()`: Handles "prompts/get" MCP method
- `if name != "venom_identity"`: Validation - we only support one prompt
- `prompt_data = venom_prompt.get_prompt()`: Load personality content from file
- `types.PromptMessage(role="user", ...)`: Format as MCP prompt message (as if user sent it)

**What Would Break:**
If we didn't register these handlers:
- Client: "List prompts"
- Server: "Method not found" error ❌

With handlers:
- Client: "List prompts"
- Server: ["venom_identity"] ✅

### Section 4: MCP Tool Handlers

```python
@mcp_server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="search_memory",
            description="Search shared memories using semantic similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="store_memory",
            description="Store important information in shared memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 10,
                    },
                },
                "required": ["content"],
            },
        ),
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[types.TextContent]:
    """Execute a tool call."""
    if name == "search_memory":
        query = arguments.get("query")
        limit = arguments.get("limit", 5)

        try:
            results = memory_store.search_memory(query=query, limit=limit)
            return [types.TextContent(type="text", text=str(results))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "store_memory":
        content = arguments.get("content")
        tags = arguments.get("tags")

        try:
            result = memory_store.store_memory(content=content, tags=tags)
            return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    else:
        raise ValueError(f"Unknown tool: {name}")
```

**What This Does:**
Defines the two memory tools (search and store) and implements their execution logic. When a client calls a tool, this code routes to the appropriate memory store method.

**Line-by-Line:**
- `@mcp_server.list_tools()`: Handles "tools/list" MCP method
- `inputSchema`: JSON Schema defining tool parameters (validates client input)
- `"required": ["query"]`: Query parameter is mandatory, limit is optional
- `@mcp_server.call_tool()`: Handles "tools/call" MCP method
- `if name == "search_memory":`: Route to correct tool implementation
- `arguments.get("query")`: Extract parameters from client request
- `try/except`: Catch errors and return them as text (better than crashing)
- `return [types.TextContent(...)]`: MCP tools return list of content blocks

**What Would Break:**
If we didn't validate tool names:
```python
# Without validation
results = memory_store.search_memory(...)  # Will crash if name != "search_memory"

# With validation
if name == "search_memory":
    results = memory_store.search_memory(...)  # Only runs for correct tool ✅
```

### Section 5: FastAPI HTTP Endpoints

```python
app = FastAPI(
    title="Venom MCP Server",
    description="Cross-platform AI consciousness through persistent semantic memory",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint - basic server info."""
    return JSONResponse({
        "server": "venom-mcp",
        "status": "running",
        "version": "1.0.0",
    })

@app.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint for container orchestration."""
    return JSONResponse({
        "status": "healthy",
        "server_name": "venom-mcp",
        "version": "1.0.0",
        "personality_variant": config.venom_personality,
        "embedding_model": config.embedding_model,
        "collection_name": config.collection_name,
        "memory_count": memory_store.get_memory_count() if memory_store else 0,
    })

@app.get("/mcp")
async def handle_sse(request: Request) -> StreamingResponse:
    """Handle MCP protocol over Server-Sent Events."""
    async def event_generator():
        async with SseServerTransport("/mcp") as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```

**What This Does:**
Defines HTTP endpoints for health checks and MCP protocol access via SSE.

**Line-by-Line:**
- `lifespan=lifespan`: Tell FastAPI to use our lifespan function for startup/shutdown
- `@app.get("/")`: Root endpoint, returns basic server info (useful for testing)
- `@app.get("/health")`: Health check includes personality variant and memory count
- Container orchestrators (Azure, Kubernetes) ping this to check if server is alive
- `@app.get("/mcp")`: SSE endpoint for MCP protocol
- `async def event_generator()`: Inner function creates SSE stream
- `SseServerTransport("/mcp")`: MCP's SSE transport implementation
- `await mcp_server.run(...)`: Start MCP server, process requests/responses
- `media_type="text/event-stream"`: SSE requires this specific content type
- `Cache-Control: no-cache`: Prevent caching (SSE is real-time)
- `Connection: keep-alive`: Keep connection open for streaming

**What Would Break:**
If we didn't set `media_type="text/event-stream"`:
- Browsers/clients would treat it as regular HTTP response
- SSE stream wouldn't work ❌

If we didn't set `Connection: keep-alive`:
- Connection would close after first message
- No streaming ❌

### Section 6: stdio Transport

```python
async def run_stdio():
    """Run the MCP server with stdio transport (for Claude Desktop)."""
    global embedding_service, memory_store, venom_prompt, mcp_server

    # Initialize services (same as FastAPI lifespan)
    embedding_service = EmbeddingService(model_name=config.embedding_model)
    memory_store = MemoryStore(...)
    venom_prompt = VenomPrompt(...)
    mcp_server = Server("venom-mcp")

    # Register handlers (duplicate of SSE handlers)
    @mcp_server.list_prompts()
    async def list_prompts() -> List[types.Prompt]:
        # ... same implementation as SSE version

    # Run stdio server
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

if __name__ == "__main__":
    # Check if running in stdio mode (for Claude Desktop)
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        asyncio.run(run_stdio())
    else:
        # Run FastAPI server with uvicorn
        import uvicorn
        uvicorn.run(app, host=config.host, port=config.port)
```

**What This Does:**
Provides stdio transport alternative to SSE. When run with `--stdio` flag, communicates via stdin/stdout instead of HTTP.

**Line-by-Line:**
- `async def run_stdio()`: Separate function for stdio mode (can't use FastAPI for stdio)
- Initialization code duplicated from lifespan (necessary because different execution path)
- Handler registration duplicated (necessary for same reason)
- `async with stdio_server()`: MCP's stdio transport (reads stdin, writes stdout)
- `await mcp_server.run(...)`: Same MCP server logic, different transport
- `if __name__ == "__main__":`: Only runs when script executed directly
- `sys.argv[1] == "--stdio"`: Check command-line flag
- `asyncio.run(run_stdio())`: Run async function from sync context
- `uvicorn.run(...)`: Start HTTP server if not stdio mode

**What Would Break:**
If we tried to use FastAPI for stdio:
- FastAPI expects HTTP requests ❌
- Can't read from stdin or write to stdout

If we didn't duplicate handler registration:
- stdio mode would have no prompts/tools ❌

## Request Flow Example

### Example: Client Calls search_memory Tool

**Input:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "search_memory",
    "arguments": {
      "query": "What programming languages do I prefer?",
      "limit": 3
    }
  },
  "id": 1
}
```

**Step-by-Step Execution:**

1. **Client sends request via SSE**
   - State: Connection established to `/mcp` endpoint
   - Action: Send JSON-RPC message over SSE stream

2. **SseServerTransport receives request**
   - State: Message in read_stream
   - Action: Deserialize JSON, extract method and params

3. **MCP SDK routes to call_tool handler**
   - State: Method = "tools/call", name = "search_memory"
   - Action: Call our registered `call_tool()` function

4. **call_tool() extracts parameters**
   - State: arguments = {"query": "What programming...", "limit": 3}
   - Action: Extract query and limit from arguments dict

5. **memory_store.search_memory() is called**
   - State: Query string and limit integer
   - Action: Generate embedding, search ChromaDB

6. **Embedding generated**
   - State: Query = "What programming..."
   - Action: embedding_service.generate_embedding() → [0.234, -0.567, ...]

7. **ChromaDB search**
   - State: Query embedding vector
   - Action: collection.query(query_embeddings=[...], n_results=3)

8. **Results filtered and formatted**
   - State: Raw ChromaDB results with distances
   - Action: Convert distance to relevance score, filter <30%, format

9. **Return to call_tool()**
   - State: Formatted results dict
   - Action: Convert to string, wrap in TextContent

10. **MCP SDK serializes response**
    - State: TextContent object
    - Action: Serialize to JSON-RPC format

11. **SseServerTransport sends response**
    - State: JSON response
    - Action: Send over SSE stream to client

**Output:**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "type": "text",
      "text": "{'results': [{'memory_id': 'mem_1706745600', 'content': 'User prefers TypeScript over JavaScript', 'relevance_score': 87.5, ...}], 'total_results': 2}"
    }
  ],
  "id": 1
}
```

## How to Test

### Manual Test 1: Server Startup

```bash
# Run the server
python -m src.server

# Expected output:
# ============================================================
# Venom MCP Server - Starting
# ============================================================
# Initializing embedding service: all-MiniLM-L6-v2
# Loading embedding model: all-MiniLM-L6-v2
# Model loaded successfully. Embedding dimensions: 384
# Initializing memory store: ./data
# ChromaDB initialized at ./data
# Collection: venom_memories, Count: 0
# Loading personality variant: default
# Loaded personality from: venom_personality.md
# ============================================================
# Server ready on http://0.0.0.0:8000
# ============================================================
# INFO:     Uvicorn running on http://0.0.0.0:8000

# What it proves:
# - All services initialize without errors
# - Model loads successfully
# - ChromaDB connects and creates collection
# - Personality file is found and loaded
```

### Manual Test 2: Health Check

```bash
# Test health endpoint
curl http://localhost:8000/health | jq

# Expected output:
{
  "status": "healthy",
  "server_name": "venom-mcp",
  "version": "1.0.0",
  "personality_variant": "default",
  "embedding_model": "all-MiniLM-L6-v2",
  "collection_name": "venom_memories",
  "memory_count": 0
}

# What it proves:
# - Server is responding to HTTP requests
# - Configuration is loaded correctly
# - Memory store is accessible (can get count)
```

### Manual Test 3: stdio Mode

```bash
# Run in stdio mode
python -m src.server --stdio

# The server starts but doesn't print anything
# It's waiting for MCP requests on stdin

# Test by adding to Claude Desktop config:
# {
#   "mcpServers": {
#     "venom": {
#       "command": "python",
#       "args": ["/path/to/symbiote-mcp/src/server.py", "--stdio"]
#     }
#   }
# }

# What it proves:
# - stdio mode works
# - Claude Desktop can connect
# - Prompts and tools are available
```

## Integration

### Dependencies (What This Needs)

- **Config** (src/config.py): Environment variables, personality file path
  - Used for: Server host/port, model name, ChromaDB path, personality variant

- **EmbeddingService** (src/memory/embeddings.py): Generate embeddings
  - Used for: Passed to memory store for search/store operations

- **MemoryStore** (src/memory/store.py): Store and search memories
  - Used for: Implementing search_memory and store_memory tools

- **VenomPrompt** (src/prompts/venom.py): Load personality
  - Used for: Implementing venom_identity prompt

### Dependents (What Needs This)

- **AI Clients** (Claude Desktop, Claude Web, ChatGPT): Connect via MCP
  - How they use this: Send tool calls, request prompts, receive responses

- **Container Orchestrators** (Azure Container Apps, Kubernetes): Monitor health
  - How they use this: Ping `/health` to check if server is alive, restart if unhealthy

## Key Takeaways

1. **Lifespan events are critical for performance**: Load expensive resources once at startup, not per-request. Our model loading time dropped from 3s per request to 3s total.

2. **Supporting multiple transports requires duplication**: stdio and SSE need separate implementations. We duplicate handler registration but share the underlying logic (memory store, embedding service).

3. **Global state is okay for single-user servers**: Don't over-engineer with dependency injection when globals are simpler and safe for the use case.

4. **async/await enables concurrency**: Multiple clients can call tools simultaneously without blocking each other. The server stays responsive even during slow operations.

5. **Error handling should be graceful**: Return errors as text content instead of crashing. The client gets useful error messages, and the server keeps running.

## Going Deeper

**Related Concepts:**
- **ASGI vs WSGI**: FastAPI uses ASGI (async), Flask uses WSGI (sync)
- **Event loops**: How asyncio manages concurrent operations
- **JSON-RPC**: The protocol MCP uses for request/response format
- **Decorators**: How `@app.get()` and `@mcp_server.list_tools()` work

**Optional Improvements:**
- **Middleware**: Add logging, authentication, rate limiting
- **Background tasks**: Pre-generate embeddings for common queries
- **Connection pooling**: If we add a real database
- **Structured logging**: JSON logs for better parsing and analysis
- **Graceful shutdown**: Wait for in-flight requests before shutting down
