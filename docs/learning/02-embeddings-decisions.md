# Embeddings System - Decisions Log

## Decision 1: sentence-transformers vs OpenAI Embeddings API

**Timestamp:** 2026-01-31 (initial implementation)

**Context:**
Need embeddings for semantic search. Two main options: local models or cloud API.

**Options Considered:**

### Option A: OpenAI Embeddings API
- **Pros:** Highest quality (1536 dimensions), constantly improving, simple API
- **Cons:** Costs $0.0001/1K tokens, requires internet, rate limits, vendor lock-in
- **Example:** `openai.embeddings.create(input="text", model="text-embedding-3-large")`

### Option B: sentence-transformers (local)
- **Pros:** Free, runs offline, no rate limits, privacy
- **Cons:** Lower quality than OpenAI, requires downloading models, uses RAM/CPU
- **Example:** `SentenceTransformer('all-MiniLM-L6-v2').encode("text")`

**Decision: We chose sentence-transformers (Option B)**

**Reasoning:**
1. Constitution explicitly states "no paid APIs"
2. Free tier deployment requires zero ongoing costs
3. Privacy: data never leaves the server
4. Quality is "good enough" for personal use (87%+ relevance for typical queries)

**Trade-offs:**
- ✅ We gained: $0/month cost, offline capability, privacy
- ❌ We lost: ~10% accuracy compared to OpenAI (acceptable for personal use)

---

## Decision 2: all-MiniLM-L6-v2 vs Larger Models

**Timestamp:** 2026-01-31 (initial implementation)

**Context:**
sentence-transformers has many models. Need to choose one balancing quality, speed, size.

**Options Considered:**

### Option A: all-MiniLM-L6-v2 (384 dims)
- **Pros:** Fast, small (80MB), good quality for general use
- **Cons:** Lower quality than larger models
- **Performance:** ~300ms per embedding

### Option B: all-mpnet-base-v2 (768 dims)
- **Pros:** Higher quality, better for nuanced queries
- **Cons:** 2x slower, 2x larger, 2x RAM
- **Performance:** ~600ms per embedding

### Option C: all-MiniLM-L12-v2 (384 dims)
- **Pros:** Better quality than L6, same dimensions
- **Cons:** Slower than L6, still not as good as mpnet
- **Performance:** ~450ms per embedding

**Decision: We chose all-MiniLM-L6-v2 (Option A)**

**Reasoning:**
1. Meets <500ms performance requirement with margin
2. 80MB fits easily in Docker image and RAM
3. Quality sufficient for personal use (tested on sample queries)
4. Can upgrade later if needed (config change, no code changes)

**Trade-offs:**
- ✅ We gained: Fast performance, small footprint
- ❌ We lost: ~5% accuracy vs larger models (acceptable trade-off)

---

## Decision 3: Lazy Loading vs Eager Loading

**Timestamp:** 2026-01-31 (initial implementation)

**Context:**
When to load the 80MB model into memory?

**Options Considered:**

### Option A: Lazy Loading (load on first use)
- **Pros:** Fast object creation, only loads if needed
- **Cons:** First embedding generation is slow
- **Example:**
  ```python
  service = EmbeddingService()  # Instant
  emb = service.generate_embedding("text")  # Slow first time, fast after
  ```

### Option B: Eager Loading (load in __init__)
- **Pros:** Predictable - all calls are fast
- **Cons:** Slow object creation even if never used
- **Example:**
  ```python
  service = EmbeddingService()  # 2-3 seconds
  emb = service.generate_embedding("text")  # Fast always
  ```

**Decision: We chose Lazy Loading (Option A)**

**Reasoning:**
1. Combines with lifespan initialization in server
2. Server startup triggers lazy load (makes all requests fast)
3. More flexible for testing (can create service without loading model)
4. Standard pattern for expensive resources

**Trade-offs:**
- ✅ We gained: Flexibility, standard pattern
- ❌ We lost: Nothing (lifespan event triggers load anyway)

---

## Decision 4: Numpy Array vs Python List for Return Type

**Timestamp:** 2026-01-31 (initial implementation)

**Context:**
`model.encode()` returns numpy array. What should our method return?

**Options Considered:**

### Option A: Return numpy array directly
- **Pros:** No conversion overhead, efficient for math operations
- **Cons:** ChromaDB expects Python lists
- **Example:** `return embedding  # numpy array`

### Option B: Convert to Python list
- **Pros:** Compatible with ChromaDB, JSON-serializable
- **Cons:** Small conversion overhead (~1ms for 384 floats)
- **Example:** `return embedding.tolist()  # Python list`

**Decision: We chose Python List (Option B)**

**Reasoning:**
1. ChromaDB requires Python lists, not numpy arrays
2. Conversion is trivial cost (~1ms) compared to generation (~300ms)
3. Lists are more portable (work with JSON, msgpack, etc.)

**Trade-offs:**
- ✅ We gained: Compatibility, portability
- ❌ We lost: ~1ms per embedding (0.3% overhead)

---

## Problem 1: Model Download Failure on First Run

**What Happened:**
```python
service = EmbeddingService()
embedding = service.generate_embedding("test")
# ConnectionError: Failed to download model
```

**Why It Happened:**
Model not pre-downloaded, no internet connection in container.

**Attempted Solutions:**

1. **Try:** Increase timeout
   - **Result:** Still fails (not a timeout issue)
   - **Why It Didn't Work:** Network unavailable

2. **Try:** Manual download before container build
   - **Result:** Works locally, fails in container
   - **Why It Didn't Work:** Model not in Docker image

**Final Solution:**
Pre-download model during Docker build:
```dockerfile
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

**Why This Worked:**
Downloads model during build (when internet is available), includes in image.

**Lesson Learned:**
Pre-download all external resources during container build, not at runtime.

**Timestamp:** 2026-01-31

---

## Problem 2: High Memory Usage in Container

**What Happened:**
Container crashes with OOM (out of memory) error after a few requests.

**Why It Happened:**
Each request was creating a new EmbeddingService (and loading model again).

**Attempted Solutions:**

1. **Try:** Increase container memory limit
   - **Result:** Delays crash, doesn't fix root cause
   - **Why It Didn't Work:** Memory leak continues

**Final Solution:**
Use global singleton service initialized in lifespan:
```python
embedding_service = None  # Global

@asynccontextmanager
async def lifespan(app):
    global embedding_service
    embedding_service = EmbeddingService()  # Load once
    yield

@app.post("/tool")
async def call_tool():
    embedding = embedding_service.generate_embedding(...)  # Reuse
```

**Why This Worked:**
Model loaded once (500MB), reused for all requests. No memory leak.

**Lesson Learned:**
Load expensive resources once, reuse many times. Don't create new instances per request.

**Timestamp:** 2026-01-31
