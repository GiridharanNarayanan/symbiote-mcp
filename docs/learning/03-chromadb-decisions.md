# ChromaDB Memory Store - Decisions Log

## Decision 1: Timestamp-based IDs vs UUIDs

**Context:** Need unique IDs for each memory.

**Decision:** Timestamp-based (`mem_1706745600`)

**Reasoning:**
- Chronological ordering built-in
- Readable and debuggable
- Single-user server (no collision risk)
- Simpler than UUID generation

**Trade-offs:**
- ✅ Gained: Chronological, readable, simple
- ❌ Lost: Unpredictability (minor security concern, not relevant for single-user)

## Decision 2: 30% Relevance Threshold

**Context:** Should we filter low-relevance search results?

**Decision:** Filter results < 30% relevance

**Reasoning:**
- Tested on sample queries
- < 30% are typically noise/false positives
- Improves UX by showing only relevant results
- Users can adjust limit if needed

**Trade-offs:**
- ✅ Gained: Higher quality results
- ❌ Lost: Some edge cases filtered (acceptable)

## Decision 3: Tags as Comma-Separated String

**Context:** ChromaDB metadata only supports primitives (string, number, bool).

**Decision:** Store array as comma-separated string

**Reasoning:**
- ChromaDB constraint (can't store arrays directly)
- Simple to split on retrieval
- Comma is unlikely in tags
- Alternative (JSON string) is overkill

**Trade-offs:**
- ✅ Gained: Simplicity, works with ChromaDB
- ❌ Lost: Clean data structure (but retrieval handles it)

## Problem 1: ChromaDB Directory Permissions

**What Happened:** Container fails to write to `/app/data`

**Solution:** 
- Ensure directory created with proper permissions
- Use `mkdir -p` in Dockerfile
- Mount persistent volume with correct user

**Lesson:** Always create directories in Dockerfile, don't rely on runtime creation
