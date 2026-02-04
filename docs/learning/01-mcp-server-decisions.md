# MCP Server - Decisions Log

## Decision 1: FastAPI vs Flask vs Custom ASGI

**Timestamp:** 2026-01-31 (initial implementation)

**Context:**
Need to choose a Python web framework to build the MCP server. Requirements:
- Must support async/await (constitutional requirement)
- Must support Server-Sent Events for remote clients
- Must be fast enough for real-time AI interactions
- Should be simple to understand (educational value)

**Options Considered:**

### Option A: Flask
- **Pros:**
  - Mature ecosystem, lots of resources
  - Simple and well-documented
  - Many developers familiar with it
- **Cons:**
  - No native async support (needs Flask-Async extension)
  - SSE requires additional libraries (Flask-SSE)
  - WSGI (synchronous) not ASGI (asynchronous)
- **Example:**
  ```python
  from flask import Flask
  from flask_sse import sse

  app = Flask(__name__)
  app.config["REDIS_URL"] = "redis://localhost"
  app.register_blueprint(sse, url_prefix='/stream')
  ```

### Option B: FastAPI
- **Pros:**
  - Native async/await support
  - Built-in type hints and validation
  - SSE via StreamingResponse (no extra dependencies)
  - Automatic API documentation
  - Fast performance (on par with Node.js)
- **Cons:**
  - Newer (less mature than Flask)
  - Smaller ecosystem
- **Example:**
  ```python
  from fastapi import FastAPI
  from fastapi.responses import StreamingResponse

  app = FastAPI()

  @app.get("/stream")
  async def stream():
      async def event_generator():
          yield "data: hello\n\n"
      return StreamingResponse(event_generator(), media_type="text/event-stream")
  ```

### Option C: Custom ASGI Implementation
- **Pros:**
  - Maximum control and performance
  - No framework overhead
  - Minimal dependencies
- **Cons:**
  - Reinventing the wheel
  - More code to maintain
  - Harder to understand for learners
- **Example:**
  ```python
  async def app(scope, receive, send):
      if scope['type'] == 'http':
          # Manual request parsing, routing, response building
          ...
  ```

**Decision: We chose FastAPI (Option B)**

**Reasoning:**
1. **async/await is non-negotiable**: Constitution requires it, FastAPI has it built-in
2. **SSE support is clean**: StreamingResponse works perfectly, no Redis dependency
3. **Type hints improve reliability**: Pydantic validation catches errors early
4. **Educational value**: Modern best practices, good example for learners
5. **Performance sufficient**: <500ms response time requirement easily met

**Trade-offs:**
- ✅ We gained: Native async, type safety, clean SSE, automatic docs
- ❌ We lost: Some Flask ecosystem libraries (but we don't need them)

---

## Decision 2: Global State vs Dependency Injection

**Timestamp:** 2026-01-31 (initial implementation)

**Context:**
Services (embedding_service, memory_store, venom_prompt) need to be accessible in request handlers. Two patterns:
1. Global variables initialized at startup
2. FastAPI dependency injection

**Options Considered:**

### Option A: Global Variables
- **Pros:**
  - Simple and straightforward
  - Easy to understand
  - No extra code
- **Cons:**
  - Harder to test (can't mock easily)
  - Global state is generally frowned upon
- **Example:**
  ```python
  embedding_service = None

  @asynccontextmanager
  async def lifespan(app):
      global embedding_service
      embedding_service = EmbeddingService()
      yield

  @app.get("/tool")
  async def call_tool():
      result = embedding_service.generate_embedding("test")
  ```

### Option B: Dependency Injection
- **Pros:**
  - Testable (can inject mocks)
  - "Proper" design pattern
  - FastAPI supports it well
- **Cons:**
  - More boilerplate code
  - Harder for beginners to understand
  - Overkill for single-user server
- **Example:**
  ```python
  def get_embedding_service() -> EmbeddingService:
      return embedding_service

  @app.get("/tool")
  async def call_tool(
      embedding_service: EmbeddingService = Depends(get_embedding_service)
  ):
      result = embedding_service.generate_embedding("test")
  ```

**Decision: We chose Global Variables (Option A)**

**Reasoning:**
1. **Single-user server**: No multi-tenancy, global state is safe
2. **Simpler code**: Easier to read and understand for learners
3. **No testing in Phase 1**: Manual testing only (per constitution)
4. **Services are immutable**: Only written at startup, read during requests

**Trade-offs:**
- ✅ We gained: Simpler code, easier to understand
- ❌ We lost: Testability (but not needed in Phase 1)

**Note for future:** If we add automated tests in Phase 2, can refactor to dependency injection.

---

## Decision 3: Duplicate Handlers for stdio vs SSE

**Timestamp:** 2026-01-31 (initial implementation)

**Context:**
MCP server needs to support two transports:
- SSE for remote clients (Claude Web, ChatGPT)
- stdio for local clients (Claude Desktop)

FastAPI can't handle stdio, so we need separate code paths.

**Options Considered:**

### Option A: Duplicate Handler Registration
- **Pros:**
  - Each transport is self-contained
  - Easy to understand
  - No complex abstraction
- **Cons:**
  - Code duplication (~50 lines)
  - Handler logic appears twice
- **Example:**
  ```python
  # In lifespan (for SSE)
  @mcp_server.list_tools()
  async def list_tools():
      return [Tool(...)]

  # In run_stdio() (for stdio)
  @mcp_server.list_tools()
  async def list_tools():
      return [Tool(...)]  # Same code
  ```

### Option B: Shared Handler Functions
- **Pros:**
  - No duplication
  - Single source of truth
- **Cons:**
  - More complex (need to define handlers separately, register twice)
  - Harder to understand
- **Example:**
  ```python
  async def list_tools_impl():
      return [Tool(...)]

  def register_handlers(server):
      @server.list_tools()
      async def list_tools():
          return await list_tools_impl()

  # In lifespan
  register_handlers(mcp_server)

  # In run_stdio
  register_handlers(mcp_server)
  ```

**Decision: We chose Duplicate Handler Registration (Option A)**

**Reasoning:**
1. **Simplicity over DRY**: Educational value of clear, self-contained code
2. **Handlers are small**: ~50 lines total, not massive duplication
3. **Independent evolution**: stdio and SSE might diverge in future
4. **Easier debugging**: Each transport has its own handler to inspect

**Trade-offs:**
- ✅ We gained: Clarity, independence, easier debugging
- ❌ We lost: Some duplication (but manageable amount)

---

## Decision 4: Lifespan Events vs On-Request Initialization

**Timestamp:** 2026-01-31 (initial implementation)

**Context:**
Embedding model is 80MB and takes 2-3 seconds to load. When to load it?
- At server startup (lifespan event)
- On first request (lazy loading)

**Options Considered:**

### Option A: Lifespan Event (Startup)
- **Pros:**
  - All requests are fast (no wait for model)
  - Predictable startup time
  - Fails fast if model missing
- **Cons:**
  - Slower server startup (3-5 seconds)
  - Model loaded even if never used
- **Example:**
  ```python
  @asynccontextmanager
  async def lifespan(app):
      embedding_service = EmbeddingService()  # Loads model now
      yield
  ```

### Option B: Lazy Loading (First Request)
- **Pros:**
  - Fast server startup
  - Only loads if needed
- **Cons:**
  - First request is very slow (3+ seconds)
  - Unpredictable first-request latency
  - User has bad first experience
- **Example:**
  ```python
  embedding_service = None

  async def get_embedding_service():
      global embedding_service
      if embedding_service is None:
          embedding_service = EmbeddingService()  # Loads on first call
      return embedding_service
  ```

**Decision: We chose Lifespan Event (Option A)**

**Reasoning:**
1. **User experience**: First request is as fast as subsequent ones
2. **Fail fast**: If model is missing, server won't start (better than first request failing)
3. **Startup only happens once**: 3-5 seconds once vs 3-5 seconds on every cold start
4. **Predictable performance**: No surprises for users

**Trade-offs:**
- ✅ We gained: Consistent performance, better UX, fail fast
- ❌ We lost: Slower startup (but happens once per deployment)

---

## Decision 5: String Serialization for Tool Results

**Timestamp:** 2026-01-31 (initial implementation)

**Context:**
Tool results need to be returned to MCP client. MCP expects `List[types.TextContent]`. How to format the search results?

**Options Considered:**

### Option A: JSON String
- **Pros:**
  - Structured data
  - Easy to parse on client side
  - Standard format
- **Cons:**
  - Need to serialize dict to JSON
  - Extra import (json module)
- **Example:**
  ```python
  import json
  results = memory_store.search_memory(...)
  return [types.TextContent(type="text", text=json.dumps(results))]
  ```

### Option B: Python str() Conversion
- **Pros:**
  - Simplest code
  - No extra imports
  - Works for MVP
- **Cons:**
  - Not standard format
  - Client needs to parse Python dict string
  - Harder for non-Python clients
- **Example:**
  ```python
  results = memory_store.search_memory(...)
  return [types.TextContent(type="text", text=str(results))]
  ```

### Option C: Custom Formatting
- **Pros:**
  - Human-readable
  - Pretty output
- **Cons:**
  - Hard to parse programmatically
  - Inconsistent format
- **Example:**
  ```python
  results = memory_store.search_memory(...)
  formatted = "\n".join(f"- {r['content']} ({r['relevance_score']}%)" for r in results)
  return [types.TextContent(type="text", text=formatted)]
  ```

**Decision: We chose Python str() Conversion (Option B)**

**Reasoning:**
1. **Simplest for MVP**: Gets us working quickly
2. **Client is Python-based**: Claude's MCP client can parse it
3. **Can improve later**: Phase 2 can add JSON serialization
4. **No breaking changes**: Adding JSON later won't break existing behavior

**Trade-offs:**
- ✅ We gained: Simplicity, fewer dependencies
- ❌ We lost: Standard format (but can add in Phase 2)

---

## Problem 1: MCP SDK Import Error

**What Happened:**
```python
from mcp import types
# ModuleNotFoundError: No module named 'mcp'
```

**Why It Happened:**
MCP SDK wasn't installed in virtual environment.

**Attempted Solutions:**

1. **Try:** `pip install mcp`
   - **Result:** `ERROR: Could not find a version that satisfies the requirement mcp`
   - **Why It Didn't Work:** Package name is different from import name

2. **Try:** Check MCP documentation for package name
   - **Result:** Found correct package name is `mcp` but need specific version
   - **Why It Didn't Work:** Still used wrong package name

**Final Solution:**
```bash
pip install mcp>=1.0.0
```

**Why This Worked:**
MCP Python SDK is published as `mcp` on PyPI, need version 1.0.0 or higher for Server class.

**Lesson Learned:**
Always check official documentation for correct package names. Import name doesn't always match package name (e.g., `import PIL` but `pip install pillow`).

**Timestamp:** 2026-01-31

---

## Problem 2: SSE Connection Closes Immediately

**What Happened:**
Client connects to `/mcp` endpoint, but connection closes after 1 second. No MCP messages received.

**Why It Happened:**
Didn't set correct headers for SSE streaming.

**Attempted Solutions:**

1. **Try:** Return StreamingResponse without special headers
   - **Result:** Connection closes immediately
   - **Why It Didn't Work:** Browser/client doesn't know this is a stream

2. **Try:** Add `Connection: keep-alive` header
   - **Result:** Connection stays open longer, but still no data
   - **Why It Didn't Work:** Missing `Cache-Control` header

**Final Solution:**
```python
return StreamingResponse(
    event_generator(),
    media_type="text/event-stream",  # Critical!
    headers={
        "Cache-Control": "no-cache",  # Prevent caching
        "Connection": "keep-alive",   # Keep connection open
    },
)
```

**Why This Worked:**
- `media_type="text/event-stream"`: Tells client this is SSE
- `Cache-Control: no-cache`: Prevents proxies from caching stream
- `Connection: keep-alive`: Keeps TCP connection open

**Lesson Learned:**
SSE requires specific headers to work correctly. Without them, HTTP defaults to close connections after response.

**Timestamp:** 2026-01-31

---

## Code Evolution

### Version 1: Inline Handler Registration

**Initial approach:**
```python
app = FastAPI()

@app.get("/mcp")
async def handle_mcp():
    # MCP logic inline
    if request.method == "tools/list":
        return [...]
    elif request.method == "tools/call":
        return ...
```

**Problem:** Mixing HTTP routing with MCP protocol logic.

### Version 2: Separate MCP Server

**Improvement:**
```python
app = FastAPI()
mcp_server = Server("venom-mcp")

@mcp_server.list_tools()
async def list_tools():
    return [...]

@app.get("/mcp")
async def handle_mcp():
    # Delegate to MCP server
    await mcp_server.run(...)
```

**What changed:** Separated HTTP transport (FastAPI) from protocol logic (MCP server).

**Why it's better:**
- MCP handlers are independent of transport
- Same handlers work for stdio and SSE
- Clearer separation of concerns

### Version 3: Lifespan Initialization

**Improvement:**
```python
@asynccontextmanager
async def lifespan(app):
    # Initialize services once
    global embedding_service
    embedding_service = EmbeddingService()
    yield

app = FastAPI(lifespan=lifespan)
```

**What changed:** Moved initialization from inline to lifespan event.

**Why it's better:**
- Model loads once at startup (fast requests)
- Predictable startup behavior
- Resources cleaned up on shutdown
