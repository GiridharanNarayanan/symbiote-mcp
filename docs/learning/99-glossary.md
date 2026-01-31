# Glossary - Venom MCP Server

All technical terms explained in simple language.

---

## A

### ASGI (Asynchronous Server Gateway Interface)
A standard for Python web servers that handle many requests at once without blocking. Think of it like a restaurant where waiters can take multiple orders simultaneously instead of waiting for each dish to be ready before taking the next order.

### async/await
Python keywords for writing code that can do multiple things at once. Instead of waiting for a slow operation (like database query) to finish, the program can work on something else and come back later.

**Example:**
```python
# Without async - waits 5 seconds doing nothing
result = slow_database_query()  # Blocks for 5 seconds
print(result)

# With async - can handle other requests during those 5 seconds
result = await slow_database_query()  # Yields control while waiting
print(result)
```

### Azure Container Apps
A cloud service that runs Docker containers. Key feature: **scale-to-zero** - automatically shuts down when not in use (costs $0), wakes up in ~2 seconds when needed.

---

## C

### ChromaDB
An embedded vector database that stores embeddings and performs semantic search. "Embedded" means it runs inside your application (no separate server needed), stores data in a local file.

### Collection
A group of related items in ChromaDB. Like a folder for files, but for embeddings. Our server uses one collection called `venom_memories` to store all memories.

### Cosine Similarity
A mathematical way to measure how similar two vectors are. Returns a number from -1 (opposite) to +1 (identical). We use this to find memories with similar meanings.

**Simple explanation:** Measures the angle between two vectors. Small angle = similar meanings.

---

## D

### Docker
A tool that packages your application and all its dependencies into a "container" - a standardized unit that runs the same way everywhere. Like a shipping container for code.

### Dockerfile
A recipe for building a Docker image. Lists all the steps needed to create your container (install Python, copy files, download models, etc.).

---

## E

### Embedding
A list of numbers (vector) that represents the meaning of text. Similar meanings have similar numbers. Our embeddings are 384 numbers long.

**Example:**
```
"TypeScript" → [0.234, -0.567, 0.123, ..., 0.089] (384 numbers)
"JavaScript" → [0.198, -0.523, 0.108, ..., 0.102] (very similar numbers!)
"Banana" → [-0.823, 0.234, -0.456, ..., 0.234] (very different numbers)
```

### Embedding Dimension
How many numbers are in an embedding vector. Our model produces 384-dimensional embeddings. More dimensions = more nuance captured (but slower and bigger).

---

## F

### FastAPI
A modern Python web framework with built-in async support, type checking, and automatic API documentation. We use it to build our MCP server.

---

## M

### MCP (Model Context Protocol)
A standardized way for AI assistants to access external tools and prompts. Instead of each AI platform having its own API, MCP provides one protocol that works with Claude, ChatGPT, and others.

### MCP Prompt
A reusable piece of text (like a personality definition) that the AI client can request. Our `venom_identity` prompt loads the Venom personality from a file.

### MCP Tool
A function that AI clients can call. Our tools are `search_memory` (find similar memories) and `store_memory` (save new information).

### Metadata
Extra information attached to a memory, like timestamp and tags. Helps categorize and filter memories.

---

## P

### Persistent Volume
A disk storage that survives container restarts. When the container stops/starts, data in `/app/data` persists because it's mounted from a persistent volume.

---

## S

### Scale-to-Zero
A cloud hosting feature where containers automatically shut down when idle (costs $0) and wake up quickly when needed. Perfect for low-traffic personal projects.

### Semantic Search
Searching by **meaning** instead of exact keywords. Finds "I prefer TypeScript" when you search for "What languages do I like?" even though they share no words.

**How it works:**
1. Convert query to embedding
2. Find stored embeddings that are "close" to query embedding
3. Return those memories

### sentence-transformers
A Python library for converting sentences into embeddings. We use the `all-MiniLM-L6-v2` model (80MB, 384 dimensions, good quality, free).

### Server-Sent Events (SSE)
A way for servers to send updates to clients over HTTP. The MCP protocol uses SSE to maintain a long-lived connection between the AI client and our server.

### stdio (Standard Input/Output)
Reading from keyboard and writing to screen. MCP can work over stdio for local clients (like Claude Desktop running on your computer).

---

## T

### Type Hints
Python annotations that specify what type of data a variable should hold. Helps catch bugs and makes code easier to understand.

**Example:**
```python
def search_memory(query: str, limit: int = 5) -> dict:
    # ↑ str = string, int = integer, dict = dictionary
    # These are type hints (Python doesn't enforce them, but tools can check)
```

---

## U

### Uvicorn
An ASGI server that runs FastAPI applications. It's fast, supports HTTP/2 (needed for SSE), and handles async Python code.

---

## V

### Vector
A list of numbers. In our context, it's an embedding - a list of 384 numbers representing text meaning.

**Why "vector"?** In math, a vector is a point in space with direction and magnitude. Our 384-dimensional vectors are points in a high-dimensional space where similar meanings cluster together.

### Vector Database
A specialized database optimized for storing and searching vectors. Unlike traditional databases that search for exact matches, vector databases find "similar" vectors using mathematical distance calculations.

---

## W

### We Language
Venom's personality trait of using "we" instead of "I" (since Venom is a symbiote - two beings bonded as one). Enforced via the personality file.

---

## Key Concepts in Simple Terms

### How Embeddings Capture Meaning

Imagine every word has a GPS coordinate, but instead of 2 dimensions (latitude/longitude), it has 384 dimensions:

- Dimension 1: "How technical is this?"
- Dimension 2: "How positive is this?"
- Dimension 3: "Is this about programming?"
- ... (381 more dimensions for different aspects of meaning)

Words with similar meanings have similar coordinates across all 384 dimensions.

### Why Vector Search is "Semantic"

Traditional search:
- Query: "coding preferences"
- Matches: Only memories containing those exact words
- Misses: "I prefer TypeScript" (no keyword match)

Vector search:
- Query: "coding preferences" → embedding: [0.456, -0.234, ...]
- Compare to all stored embeddings
- Finds: "I prefer TypeScript" → embedding: [0.423, -0.198, ...] (very similar!)
- Returns: This memory with 87% relevance score

### Why We Need Persistent Storage

Without persistence:
- You tell Venom "I prefer TypeScript"
- Container restarts (happens often with scale-to-zero)
- Memory lost forever ❌

With persistence:
- You tell Venom "I prefer TypeScript"
- Saved to `/app/data/chroma.sqlite3` (on persistent volume)
- Container restarts
- Memory survives! ✅

### How Scale-to-Zero Saves Money

Traditional hosting:
- Server runs 24/7 even when idle
- Cost: ~$10-30/month

Scale-to-zero:
- Server runs only when handling requests
- Personal use: Maybe 30 minutes/day
- 30min/day = 15 hours/month
- Azure free tier: 180,000 vCPU-seconds/month = 50 hours/month
- Cost: $0/month ✅

---

## Further Learning

- **Vector Embeddings**: https://jalammar.github.io/illustrated-word2vec/
- **MCP Protocol**: https://modelcontextprotocol.io/
- **FastAPI**: https://fastapi.tiangolo.com/
- **sentence-transformers**: https://www.sbert.net/
- **ChromaDB**: https://docs.trychroma.com/
- **Docker**: https://docs.docker.com/get-started/
- **Azure Container Apps**: https://learn.microsoft.com/en-us/azure/container-apps/
