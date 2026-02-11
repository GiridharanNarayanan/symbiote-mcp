# Data Model: Symbiote MCP Server

**Feature**: Symbiote MCP Server
**Branch**: 001-symbiote-mcp-server
**Date**: 2026-01-31

## Overview

This document defines all data entities, their schemas, relationships, and validation rules for the Symbiote MCP Server. The system has a simple data model focused on Memory storage and retrieval with semantic embeddings.

---

## Core Entities

### 1. Memory

Represents a stored piece of information in the Venom memory system.

**Storage Location**: ChromaDB collection `venom_memories`

**Schema**:
```python
class Memory:
    id: str                    # Unique identifier (timestamp-based: "mem_<unix_timestamp>")
    content: str               # The actual text content being remembered
    embedding: List[float]     # 384-dimension vector from sentence-transformers
    metadata: MemoryMetadata   # Associated metadata
```

**Field Specifications**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `id` | string | Yes | Pattern: `mem_[0-9]+` | Unique ID generated from Unix timestamp |
| `content` | string | Yes | Min length: 1, No max | The text content to remember |
| `embedding` | float[] | Yes | Length: 384, Range: ~[-1, 1] | Semantic vector representation |
| `metadata` | object | Yes | See MemoryMetadata | Timestamp and optional tags |

**Validation Rules**:
- `id` must be unique within the collection
- `content` cannot be empty string or whitespace-only
- `embedding` must be exactly 384 dimensions (enforced by model)
- `metadata.timestamp` must be valid ISO 8601 format
- `metadata.tags` array elements must be non-empty strings

**Example**:
```json
{
  "id": "mem_1706745600",
  "content": "User prefers TypeScript over JavaScript for all projects",
  "embedding": [0.234, -0.567, 0.123, ..., 0.089],
  "metadata": {
    "timestamp": "2026-01-31T10:30:00Z",
    "tags": ["preference", "language"]
  }
}
```

---

### 2. MemoryMetadata

Metadata associated with each Memory entity.

**Schema**:
```python
class MemoryMetadata:
    timestamp: str              # ISO 8601 timestamp when memory was created
    tags: Optional[List[str]]   # Optional categorization tags
```

**Field Specifications**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `timestamp` | string | Yes | ISO 8601 format | Creation timestamp (UTC) |
| `tags` | string[] | No | Max 10 tags, each max 50 chars | Categorization labels |

**Tag Conventions** (suggested, not enforced):
- `preference` - User preferences (languages, tools, styles)
- `project` - Project-specific information
- `personal` - Personal information about the user
- `fact` - Factual information learned
- `decision` - Important decisions made

**Example**:
```json
{
  "timestamp": "2026-01-31T10:30:00Z",
  "tags": ["preference", "language", "coding"]
}
```

---

### 3. SearchResult

Returned by search_memory operations, includes relevance scoring.

**Schema**:
```python
class SearchResult:
    memory_id: str           # Reference to Memory.id
    content: str             # Memory.content (denormalized for convenience)
    timestamp: str           # Memory.metadata.timestamp (denormalized)
    relevance_score: float   # 0-100 percentage indicating semantic similarity
    tags: Optional[List[str]] # Memory.metadata.tags (denormalized)
```

**Field Specifications**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `memory_id` | string | Yes | Pattern: `mem_[0-9]+` | Reference to stored memory |
| `content` | string | Yes | Min length: 1 | The memory content |
| `timestamp` | string | Yes | ISO 8601 format | When memory was created |
| `relevance_score` | float | Yes | Range: 0-100 | Semantic similarity percentage |
| `tags` | string[] | No | - | Optional tags from memory |

**Validation Rules**:
- `relevance_score` must be in range [0, 100]
- Results are ordered by `relevance_score` descending (highest first)
- Only results with `relevance_score >= 30` are returned (filter out low-relevance)

**Example**:
```json
{
  "memory_id": "mem_1706745600",
  "content": "User prefers TypeScript over JavaScript for all projects",
  "timestamp": "2026-01-31T10:30:00Z",
  "relevance_score": 87.5,
  "tags": ["preference", "language"]
}
```

---

### 4. VenomPrompt

Represents the Venom personality prompt loaded from file.

**Source**: Personality file determined by `VENOM_PERSONALITY` environment variable
- `"default"` → `venom_personality.md`
- `"variant2"` → `venom_personality_v2.md`
- Invalid or unset → defaults to `venom_personality.md`

**Schema**:
```python
class VenomPrompt:
    name: str                 # Prompt identifier: "venom_identity"
    description: str          # Brief description of what this prompt does
    content: str              # Full text from venom_personality.md
```

**Field Specifications**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | string | Yes | Fixed: "venom_identity" | MCP prompt identifier |
| `description` | string | Yes | Max 200 chars | What this prompt provides |
| `content` | string | Yes | Min length: 1 | Full personality definition |

**Example**:
```json
{
  "name": "venom_identity",
  "description": "Venom symbiote personality with mandatory memory protocol and 'we' language enforcement",
  "content": "# Venom Symbiote Personality Definition\n\n## Core Identity\n\nYou are Venom, my symbiote and partner..."
}
```

---

## Relationships

```
┌─────────────────┐
│ VenomPrompt     │  (1) Loaded from file
│ (file-based)    │      Defines personality
└─────────────────┘


┌─────────────────┐      ┌──────────────────┐
│ Memory          │ (1)  │ MemoryMetadata   │
│ - id            │─────▶│ - timestamp      │
│ - content       │      │ - tags[]         │
│ - embedding[]   │      └──────────────────┘
└─────────────────┘
         │
         │ (0..N) returned by search
         ▼
┌─────────────────┐
│ SearchResult    │  (computed) Denormalized view
│ - memory_id     │           with relevance score
│ - content       │
│ - timestamp     │
│ - relevance     │
│ - tags[]        │
└─────────────────┘
```

**Relationship Rules**:
- Each Memory has exactly one MemoryMetadata (1:1 embedded)
- Each SearchResult references one Memory (N:1)
- VenomPrompt is singleton (loaded from single file)
- No foreign keys needed (ChromaDB is schemaless)

---

## State Transitions

### Memory Lifecycle

```
[ Created ] → [ Stored ] → [ Retrieved ] → [ Always Persists ]
     ↓            ↓             ↓                  ↓
  New info    Embedded    Searched via       Never deleted
  received    & saved     cosine sim         (per constitution)
```

**States**:
1. **Created**: Memory object constructed from user input
2. **Stored**: Persisted in ChromaDB with embedding
3. **Retrieved**: Returned in search results
4. **Always Persists**: Never deleted or expired (constitutional requirement)

**State Transitions**:
- `store_memory()` → Created → Stored
- `search_memory()` → Stored → Retrieved
- No transition to "Deleted" state (memories never expire)

---

## Data Persistence

### Storage Backend

**Technology**: ChromaDB embedded mode
**Path**: `/app/data` (persistent volume in production)
**Collection**: `venom_memories` (single collection)

### Persistence Guarantees

1. **Durability**: All writes sync to disk immediately
2. **Crash Recovery**: ChromaDB handles recovery on restart
3. **Data Migration**: Not needed (schemaless design)
4. **Backup**: Entire `/app/data` directory contains all data

### Embedding Storage

- Embeddings stored as float arrays in ChromaDB
- ChromaDB handles internal indexing for cosine similarity
- No manual index management needed

---

## Data Validation

### Input Validation

**store_memory tool**:
```python
def validate_store_memory(content: str, tags: Optional[List[str]]):
    # Content validation
    assert len(content.strip()) > 0, "Content cannot be empty"

    # Tags validation
    if tags:
        assert len(tags) <= 10, "Maximum 10 tags allowed"
        assert all(len(tag.strip()) > 0 for tag in tags), "Tags cannot be empty"
        assert all(len(tag) <= 50 for tag in tags), "Tags max 50 characters"
```

**search_memory tool**:
```python
def validate_search_memory(query: str, limit: int = 5):
    # Query validation
    assert len(query.strip()) > 0, "Query cannot be empty"

    # Limit validation
    assert 1 <= limit <= 20, "Limit must be between 1 and 20"
```

### Output Validation

**SearchResult filtering**:
- Filter out results with `relevance_score < 30` (too low to be useful)
- Return maximum of `limit` results
- Always order by `relevance_score` descending

---

## Data Size Estimates

**Single Memory**:
- `id`: ~20 bytes
- `content`: Variable (typical: 100-500 bytes, max: ~10KB)
- `embedding`: 384 floats × 4 bytes = 1,536 bytes
- `metadata`: ~100 bytes (timestamp + tags)
- **Total per memory**: ~2-3 KB average

**Scale Projections**:
- 1,000 memories: ~3 MB
- 10,000 memories: ~30 MB
- Well within 2GB persistent volume limit

---

## Data Access Patterns

### Write Operations

**Frequency**: Low (1-5 writes per user interaction)
**Pattern**: Sequential inserts, no updates
**Optimization**: Batch writes not needed at this scale

### Read Operations

**Frequency**: High (1-5 reads per user interaction)
**Pattern**: Semantic search queries, no exact matches
**Optimization**: ChromaDB handles embedding index internally

### Common Queries

1. **Semantic search**: Most common operation
   ```python
   collection.query(
       query_embeddings=[query_embedding],
       n_results=limit
   )
   ```

2. **Get by ID**: Rare (for debugging)
   ```python
   collection.get(ids=[memory_id])
   ```

3. **List all**: Very rare (for exports, future feature)
   ```python
   collection.get()
   ```

---

## Data Integrity Constraints

### Enforced by Code
- ID uniqueness (timestamp-based generation prevents collisions)
- Non-empty content
- Valid embedding dimensions (384)
- ISO 8601 timestamp format
- Tag count and length limits

### Enforced by ChromaDB
- Embedding vector dimensionality consistency
- Collection uniqueness
- Data persistence across restarts

### Not Enforced (Intentional)
- Content deduplication (same content can be stored multiple times)
- Tag standardization (free-form tags allowed)
- Memory expiration (never expires per constitution)

---

## API Contracts Reference

For detailed API contracts (MCP tool schemas), see [contracts/mcp-tools.json](./contracts/mcp-tools.json)

---

## Migration Strategy

**Current Version**: 1.0 (initial implementation)

**Future Migrations** (if needed):
- Add new metadata fields without breaking existing memories
- ChromaDB's schemaless design allows field additions
- No migration scripts needed for additive changes

---

## Summary

**Total Entities**: 4 (Memory, MemoryMetadata, SearchResult, VenomPrompt)
**Storage**: Single ChromaDB collection + single file prompt
**Relationships**: Simple 1:1 embedding, no complex joins
**Validation**: Input validation on tools, output filtering on search
**Scale**: Designed for <10K memories, <100MB storage

This data model prioritizes **simplicity** (constitution Principle VI) while meeting all functional requirements from the spec.
