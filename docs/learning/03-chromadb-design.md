# ChromaDB Memory Store - Design

## What We're Building

A persistent vector database wrapper that stores memories with semantic embeddings and enables fast similarity search. ChromaDB handles the complex vector math (cosine similarity) and persistence, while we provide a clean interface for storing and searching memories.

**Location in architecture:** `src/memory/store.py`

**Dependencies:** chromadb, EmbeddingService

**Used by:** MCP server tools (search_memory, store_memory)

## Architecture Diagram

```
Memory Store (src/memory/store.py)
     │
     ├─► store_memory(content, tags)
     │   ↓
     │   1. Validate input
     │   2. Generate unique ID (timestamp)
     │   3. Create embedding via EmbeddingService
     │   4. Build metadata dict
     │   5. ChromaDB.add(id, embedding, content, metadata)
     │   ↓
     │   Persists to disk (/app/data/chroma.sqlite3)
     │
     └─► search_memory(query, limit)
         ↓
         1. Validate query
         2. Generate query embedding
         3. ChromaDB.query(embedding, n_results=limit)
         4. Convert distance → relevance score
         5. Filter results (relevance >= 30%)
         6. Return top N matches
```

## Why This Design?

### Technology Choice: ChromaDB Embedded Mode

**Alternatives Considered:**

1. **Pinecone/Weaviate (cloud)**
   - **Pros:** Managed, scalable, high performance
   - **Cons:** Costs money, requires internet, vendor lock-in
   - **Why rejected:** Violates "no paid APIs" requirement

2. **PostgreSQL + pgvector**
   - **Pros:** Full SQL database, ACID transactions
   - **Cons:** Need to manage PostgreSQL server, more complexity
   - **Why rejected:** Overkill for personal use, violates simplicity

3. **ChromaDB client-server mode**
   - **Pros:** Can scale to multiple clients
   - **Cons:** Need separate server process, port management
   - **Why rejected:** Single-user server, embedded is simpler

4. **FAISS (Facebook AI Similarity Search)**
   - **Pros:** Very fast, optimized for large scale
   - **Cons:** No persistence layer, need to build ourselves
   - **Why rejected:** ChromaDB provides persistence + indexing

**Why We Chose ChromaDB Embedded:**

1. **Zero operational overhead**: No separate database server to manage
2. **Persistent by default**: File-based storage, survives restarts
3. **Python-native**: Clean API, good documentation
4. **Cosine similarity built-in**: Handles vector math for us
5. **Small scale optimized**: Perfect for <10K memories

### Key Concepts

#### Concept 1: Vector Database vs Traditional Database

**Simple Explanation:**
Traditional databases find exact matches:
- SQL: `WHERE name = 'TypeScript'` → Only finds "TypeScript"
- NoSQL: `{language: "TypeScript"}` → Only finds exact match

Vector databases find similar matches:
- `query([0.234, -0.567, ...])` → Finds "TypeScript", "JavaScript", "ES6"...

They measure distance in high-dimensional space, not exact equality.

**Why It Matters:**
We search by meaning, not keywords. "What languages do I like?" should match "I prefer TypeScript" even though they share no words.

#### Concept 2: Cosine Similarity

**Simple Explanation:**
Measures angle between two vectors. Small angle = similar, large angle = different.

```
Vector A: [1, 0]  ─────►
Vector B: [0.7, 0.7]  ─────►  (45° angle)
Cosine similarity: 0.707 (similar)

Vector C: [0, 1]  │ (90° angle)
Cosine similarity: 0 (orthogonal, unrelated)

Vector D: [-1, 0]  ◄───── (180° angle)
Cosine similarity: -1 (opposite)
```

**Why It Matters:**
ChromaDB uses this to find similar memories. Higher score = more similar meaning.

#### Concept 3: Persistent Volume

**Simple Explanation:**
Regular container storage disappears when container restarts. Persistent volumes are like external hard drives that survive restarts.

```
Without persistent volume:
Container writes to /app/data → Container restarts → Data lost ❌

With persistent volume:
Container writes to /app/data → Volume saves to host disk → Container restarts → Data still there ✅
```

**Why It Matters:**
Memories must survive server restarts, container updates, and crashes.

## How It Works

### Storing a Memory

**Input:**
```python
memory_store.store_memory(
    content="User prefers TypeScript over JavaScript",
    tags=["preference", "language"]
)
```

**Process:**
1. Validate content (not empty)
2. Validate tags (max 10, each max 50 chars)
3. Generate ID: `mem_1706745600` (current Unix timestamp)
4. Generate embedding: `[0.234, -0.567, ..., 0.089]` (384 floats)
5. Create metadata: `{timestamp: "2026-01-31T10:00:00Z", tags: "preference,language"}`
6. Store in ChromaDB: `collection.add(ids=[id], embeddings=[emb], documents=[content], metadatas=[meta])`
7. ChromaDB writes to SQLite file: `/app/data/chroma.sqlite3`

**Output:**
```python
{
    "memory_id": "mem_1706745600",
    "success": True,
    "timestamp": "2026-01-31T10:00:00Z",
    "embedding_dimensions": 384
}
```

### Searching Memories

**Input:**
```python
memory_store.search_memory(
    query="What programming languages do I prefer?",
    limit=5
)
```

**Process:**
1. Validate query (not empty), validate limit (1-20)
2. Generate query embedding: `[0.198, -0.523, ..., 0.102]`
3. ChromaDB searches using cosine similarity
4. Convert distance to relevance percentage: `(1 - distance) * 100`
5. Filter out low relevance (< 30%)
6. Format results with all metadata
7. Return top N matches

**Output:**
```python
{
    "results": [
        {
            "memory_id": "mem_1706745600",
            "content": "User prefers TypeScript over JavaScript",
            "timestamp": "2026-01-31T10:00:00Z",
            "relevance_score": 87.5,
            "tags": ["preference", "language"]
        }
    ],
    "total_results": 1,
    "query_embedding_generated": True
}
```

## Edge Cases

| Scenario | How We Handle It | Why This Works |
|----------|------------------|----------------|
| **Empty content** | Raise ValueError before embedding | Fail fast, clear error message |
| **Duplicate content** | Allow (different IDs, timestamps) | User may store same info multiple times intentionally |
| **Search returns no results** | Return empty array | Valid state, not an error |
| **ChromaDB directory missing** | Create automatically | Better UX, mkdir is safe |
| **Collection doesn't exist** | Create with get_or_create_collection() | Idempotent, safe on every startup |
| **Tag with commas** | Store as is (commas in string) | Parsing handles it (split by comma) |

## What You'll Learn

- [ ] What vector databases are and how they differ from SQL/NoSQL
- [ ] How cosine similarity measures semantic similarity
- [ ] Why persistence matters for production systems
- [ ] How ChromaDB's embedded mode works
- [ ] The trade-offs between embedded and client-server databases
- [ ] How to convert distances to relevance scores
- [ ] Why filtering low-relevance results improves UX

## Design Decisions Summary

**Key Decision 1: Embedded vs Client-Server ChromaDB**
- **Trade-off:** Can't scale to multiple processes, but much simpler
- **Why it's worth it:** Single-user server, simplicity > scalability

**Key Decision 2: Timestamp-based IDs vs UUIDs**
- **Trade-off:** Predictable IDs (security risk in multi-user), but simpler
- **Why it's worth it:** Single-user, chronological IDs useful for debugging

**Key Decision 3: Store tags as comma-separated string vs array**
- **Trade-off:** Limited ChromaDB metadata (primitives only), not ideal structure
- **Why it's worth it:** Works with ChromaDB constraints, simple parsing

**Key Decision 4: 30% relevance threshold for filtering**
- **Trade-off:** Might filter some valid results, but improves quality
- **Why it's worth it:** Tested on sample queries, 30% captures good matches
