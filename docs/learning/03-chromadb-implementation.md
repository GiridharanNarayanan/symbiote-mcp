# ChromaDB Memory Store - Implementation Walkthrough

## Code Overview

**File:** `src/memory/store.py`
**Lines of Code:** ~160
**External Dependencies:** chromadb
**Internal Dependencies:** EmbeddingService

## Key Sections

### Initialization

```python
class MemoryStore:
    def __init__(self, chromadb_path: str, collection_name: str, embedding_service: EmbeddingService):
        self.chromadb_path = Path(chromadb_path)
        self.embedding_service = embedding_service
        
        # Ensure data directory exists
        self.chromadb_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.chromadb_path),
            settings=Settings(anonymized_telemetry=False),
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Venom symbiote semantic memory"},
        )
```

**What This Does:**
- Creates data directory if it doesn't exist
- Initializes ChromaDB persistent client (file-based storage)
- Creates or loads the memory collection

**Line-by-Line:**
- `Path(chromadb_path)`: Convert string to Path object for easier manipulation
- `.mkdir(parents=True, exist_ok=True)`: Create directory + parents, don't fail if exists
- `PersistentClient(path=...)`: ChromaDB client that saves to disk (vs in-memory)
- `Settings(anonymized_telemetry=False)`: Disable telemetry to Chroma servers
- `get_or_create_collection()`: Idempotent - gets existing or creates new

### Store Memory

```python
def store_memory(self, content: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    # Validate
    if not content or not content.strip():
        raise ValueError("Content cannot be empty")
    
    if tags:
        if len(tags) > 10:
            raise ValueError("Maximum 10 tags allowed")
        if any(len(tag) > 50 for tag in tags):
            raise ValueError("Tags must be maximum 50 characters")
    
    # Generate ID and embedding
    memory_id = f"mem_{int(time.time())}"
    embedding = self.embedding_service.generate_embedding(content)
    
    # Create metadata
    metadata = {"timestamp": datetime.now(timezone.utc).isoformat()}
    if tags:
        metadata["tags"] = ",".join(tags)  # Comma-separated
    
    # Store in ChromaDB
    self.collection.add(
        ids=[memory_id],
        embeddings=[embedding],
        documents=[content],
        metadatas=[metadata],
    )
    
    return {
        "memory_id": memory_id,
        "success": True,
        "timestamp": metadata["timestamp"],
        "embedding_dimensions": len(embedding),
    }
```

**What This Does:**
Validates input, generates embedding, stores in ChromaDB with metadata.

### Search Memory

```python
def search_memory(self, query: str, limit: int = 5) -> Dict[str, Any]:
    # Validate
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    if not (1 <= limit <= 20):
        raise ValueError("Limit must be between 1 and 20")
    
    # Generate query embedding
    query_embedding = self.embedding_service.generate_embedding(query)
    
    # Search ChromaDB
    results = self.collection.query(
        query_embeddings=[query_embedding],
        n_results=limit,
    )
    
    # Process results
    formatted_results = []
    if results["ids"] and results["ids"][0]:
        for idx in range(len(results["ids"][0])):
            distance = results["distances"][0][idx]
            relevance_score = max(0, (1 - distance) * 100)
            
            # Filter low relevance
            if relevance_score < 30:
                continue
            
            tags = None
            if "tags" in results["metadatas"][0][idx]:
                tags = results["metadatas"][0][idx]["tags"].split(",")
            
            formatted_results.append({
                "memory_id": results["ids"][0][idx],
                "content": results["documents"][0][idx],
                "timestamp": results["metadatas"][0][idx].get("timestamp", ""),
                "relevance_score": round(relevance_score, 1),
                "tags": tags,
            })
    
    return {
        "results": formatted_results,
        "total_results": len(formatted_results),
        "query_embedding_generated": True,
    }
```

**What This Does:**
Generates query embedding, searches ChromaDB, filters and formats results.

## Key Takeaways

1. **ChromaDB handles persistence automatically** - Just set path, it manages SQLite file
2. **Idempotent operations are safer** - get_or_create_collection works on every startup
3. **Metadata must be primitives** - Store arrays as comma-separated strings
4. **Distance ≠ Similarity** - Convert ChromaDB distance to percentage for UX
5. **Filter low relevance** - Improves result quality by removing noise
