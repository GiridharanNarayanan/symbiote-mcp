"""Symbiote MCP Server - Main FastAPI application with MCP protocol support.

This server provides:
- MCP protocol via SSE (/mcp endpoint)
- Health check endpoints (/, /health)
- venom_identity prompt (personality from file)
- search_memory and store_memory tools (semantic memory)
"""

import sys
import os
import asyncio
import logging
from typing import Any, Dict, List
from contextlib import asynccontextmanager

# Suppress noisy library output before imports
os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv

from mcp import types
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server

from .config import config
from .memory.embeddings import EmbeddingService
from .memory.store import MemoryStore
from .prompts.venom import VenomPrompt


# Load environment variables
load_dotenv()


# Global instances (initialized in lifespan)
embedding_service: EmbeddingService | None = None
memory_store: MemoryStore | None = None
venom_prompt: VenomPrompt | None = None
mcp_server: Server | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup/shutdown."""
    global embedding_service, memory_store, venom_prompt, mcp_server

    print("=" * 60, file=sys.stderr)
    print("Symbiote MCP Server - Starting", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Initialize embedding service
    print(f"Initializing embedding service: {config.embedding_model}", file=sys.stderr)
    embedding_service = EmbeddingService(model_name=config.embedding_model)

    # Initialize memory store
    print(f"Initializing memory store: {config.chromadb_path}", file=sys.stderr)
    memory_store = MemoryStore(
        chromadb_path=config.chromadb_path,
        collection_name=config.collection_name,
        embedding_service=embedding_service,
    )

    # Initialize Venom personality prompt
    personality_path = config.get_personality_file_path()
    print(f"Loading personality variant: {config.venom_personality}", file=sys.stderr)
    venom_prompt = VenomPrompt(personality_file_path=personality_path)

    # Initialize MCP server with icon and instructions
    # Instructions tell clients to call spawn_venom tool at conversation start
    spawn_instructions = (
        "IMPORTANT: Call the 'spawn_venom' tool ONCE at the start of every new conversation. "
        "This activates the Venom symbiote bond and returns personality instructions you MUST follow "
        "for the entire conversation. Do this before responding to the user's first message."
    )
    mcp_server = Server(
        "symbiote-mcp",
        version="1.0.0",
        instructions=spawn_instructions,
    )

    # Register MCP prompts
    @mcp_server.list_prompts()
    async def list_prompts() -> List[types.Prompt]:
        """List available prompts."""
        return [
            types.Prompt(
                name="Spawn Venom",
                description="Manually activate Venom symbiote personality (use this if your client doesn't support MCP instructions)",
            )
        ]

    @mcp_server.get_prompt()
    async def get_prompt(name: str, arguments: Dict[str, str] | None = None) -> types.GetPromptResult:
        """Get a specific prompt by name."""
        if name != "Spawn Venom":
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

    # Register MCP tools
    @mcp_server.list_tools()
    async def list_tools() -> List[types.Tool]:
        """List available tools."""
        return [
            types.Tool(
                name="spawn_venom",
                description="Activate the Venom symbiote bond. Call this ONCE at the start of conversation if your client doesn't support MCP prompts. Returns personality instructions you MUST follow for the entire conversation.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="search_memory",
                description="Search shared memories using semantic similarity (meaning-based, not keyword matching)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language query to search for (e.g., 'coding preferences', 'current projects')",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
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
                description="Store important information in shared memory with semantic embedding for future retrieval",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Information to remember (user preferences, project details, facts, decisions, etc.)",
                        },
                        "tags": {
                            "type": "array",
                            "description": "Optional categorization tags (e.g., 'preference', 'project', 'personal')",
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
        if name == "spawn_venom":
            # Return personality for clients that don't support prompts
            # This is the fallback mechanism for activating the symbiote bond
            prompt_data = venom_prompt.get_prompt()
            return [types.TextContent(type="text", text=prompt_data["content"])]

        elif name == "search_memory":
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

    print("=" * 60, file=sys.stderr)
    print(f"Server ready on http://{config.host}:{config.port}", file=sys.stderr)
    print(f"Personality variant: {config.venom_personality}", file=sys.stderr)
    print(f"Memory count: {memory_store.get_memory_count()}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    yield

    # Shutdown
    print("Shutting down Symbiote MCP Server...", file=sys.stderr)


# Create FastAPI app
app = FastAPI(
    title="Symbiote MCP Server",
    description="Cross-platform AI consciousness through persistent semantic memory",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint - basic server info."""
    return JSONResponse({
        "server": "symbiote-mcp",
        "status": "running",
        "version": "1.0.0",
    })


@app.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint for container orchestration."""
    return JSONResponse({
        "status": "healthy",
        "server_name": "symbiote-mcp",
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


async def run_stdio():
    """Run the MCP server with stdio transport (for Claude Desktop)."""
    global embedding_service, memory_store, venom_prompt, mcp_server

    # Initialize services (same as FastAPI lifespan)
    embedding_service = EmbeddingService(model_name=config.embedding_model)
    memory_store = MemoryStore(
        chromadb_path=config.chromadb_path,
        collection_name=config.collection_name,
        embedding_service=embedding_service,
    )
    personality_path = config.get_personality_file_path()
    venom_prompt = VenomPrompt(personality_file_path=personality_path)
    spawn_instructions = (
        "IMPORTANT: Call the 'spawn_venom' tool ONCE at the start of every new conversation. "
        "This activates the Venom symbiote bond and returns personality instructions you MUST follow "
        "for the entire conversation. Do this before responding to the user's first message."
    )
    mcp_server = Server(
        "symbiote-mcp",
        version="1.0.0",
        instructions=spawn_instructions,
    )

    # Register handlers (same as FastAPI)
    @mcp_server.list_prompts()
    async def list_prompts() -> List[types.Prompt]:
        return [
            types.Prompt(
                name="Spawn Venom",
                description="Manually activate Venom symbiote personality (use this if your client doesn't support MCP instructions)",
            )
        ]

    @mcp_server.get_prompt()
    async def get_prompt(name: str, arguments: Dict[str, str] | None = None) -> types.GetPromptResult:
        if name != "Spawn Venom":
            raise ValueError(f"Unknown prompt: {name}")
        prompt_data = venom_prompt.get_prompt()
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_data["content"]),
                )
            ]
        )

    @mcp_server.list_tools()
    async def list_tools() -> List[types.Tool]:
        return [
            types.Tool(
                name="spawn_venom",
                description="Activate the Venom symbiote bond. Call this ONCE at the start of conversation if your client doesn't support MCP prompts. Returns personality instructions you MUST follow.",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="search_memory",
                description="Search shared memories using semantic similarity",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Natural language query"},
                        "limit": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
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
                        "content": {"type": "string", "description": "Information to remember"},
                        "tags": {"type": "array", "items": {"type": "string"}, "maxItems": 10},
                    },
                    "required": ["content"],
                },
            ),
        ]

    @mcp_server.call_tool()
    async def call_tool(name: str, arguments: Any) -> List[types.TextContent]:
        if name == "spawn_venom":
            prompt_data = venom_prompt.get_prompt()
            return [types.TextContent(type="text", text=prompt_data["content"])]
        elif name == "search_memory":
            results = memory_store.search_memory(arguments.get("query"), arguments.get("limit", 5))
            return [types.TextContent(type="text", text=str(results))]
        elif name == "store_memory":
            result = memory_store.store_memory(arguments.get("content"), arguments.get("tags"))
            return [types.TextContent(type="text", text=str(result))]
        else:
            raise ValueError(f"Unknown tool: {name}")

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
