# Embeddings System - Design

## What We're Building

A system that converts text into numerical vectors (lists of numbers) that represent the meaning of the text. This lets us compare how similar two pieces of text are, even if they use completely different words. It's the foundation of semantic search - finding information by meaning rather than keywords.

**Location in architecture:** `src/memory/embeddings.py`

**Dependencies:** sentence-transformers library

**Used by:** Memory store for both storing and searching operations

## Architecture Diagram

```
User Input Text
     ↓
┌─────────────────────────────────┐
│   EmbeddingService              │
│   ┌─────────────────────────┐   │
│   │ Lazy-load model         │   │
│   │ (loads only once,       │   │
│   │  caches in memory)      │   │
│   └───────────┬─────────────┘   │
│               ↓                  │
│   ┌─────────────────────────┐   │
│   │ all-MiniLM-L6-v2        │   │
│   │ (sentence transformer)  │   │
│   │                         │   │
│   │ 80MB model file         │   │
│   │ Pre-downloaded in       │   │
│   │ Docker image            │   │
│   └───────────┬─────────────┘   │
│               ↓                  │
│   ┌─────────────────────────┐   │
│   │ .encode()               │   │
│   │ - Tokenize text         │   │
│   │ - Process through BERT  │   │
│   │ - Average token vectors │   │
│   └───────────┬─────────────┘   │
│               ↓                  │
└───────────────┼─────────────────┘
                ↓
    384-dimensional vector
    [0.234, -0.567, 0.123, ..., 0.089]
                ↓
        Used by ChromaDB for
        storage and search
```

## Why This Design?

### Technology Choice: sentence-transformers with all-MiniLM-L6-v2

**Alternatives Considered:**

1. **OpenAI Embeddings API**
   - **Pros:** Very high quality, 1536 dimensions, actively maintained
   - **Cons:** Costs $0.0001 per 1K tokens, requires internet, rate limits, vendor lock-in
   - **Why rejected:** Violates constitution's "no paid APIs" requirement, adds external dependency

2. **Word2Vec**
   - **Pros:** Fast, smaller model size, classic approach
   - **Cons:** Designed for individual words, poor at sentence-level semantics, outdated
   - **Why rejected:** Less accurate for sentences, which is our primary use case

3. **Larger BERT models (768 or 1024 dimensions)**
   - **Pros:** Higher quality embeddings, more nuance
   - **Cons:** 2-3x slower, 2-3x larger model files, minimal accuracy gain for personal use
   - **Why rejected:** Overkill for personal scale, violates "simplicity" principle

4. **Custom fine-tuned model**
   - **Pros:** Optimized for our specific use case
   - **Cons:** Requires ML expertise, training data, computational resources
   - **Why rejected:** Massive complexity increase for marginal gains

**Why We Chose sentence-transformers + all-MiniLM-L6-v2:**

1. **Free and local**: Runs entirely on your computer, no API calls, no costs, works offline
2. **Good quality**: 384 dimensions capture semantic meaning well enough for personal use
3. **Fast**: <1 second to generate embeddings for typical text (50-200 words)
4. **Industry standard**: Widely used in production systems, well-documented, actively maintained
5. **Reasonable size**: 80MB model fits easily in Docker image, loads quickly into memory
6. **Simple to use**: One function call (`model.encode(text)`) handles all complexity

### Key Concepts

#### Concept 1: Vector Embeddings

**Simple Explanation:**
Think of embeddings like GPS coordinates, but instead of 2 dimensions (latitude/longitude), we have 384 dimensions. Every word or sentence gets a location in this 384-dimensional space. Words with similar meanings are located close together.

Example:
```
"TypeScript" → [0.234, -0.567, 0.123, ..., 0.089]
"JavaScript" → [0.198, -0.523, 0.108, ..., 0.102]  ← Very close to TypeScript!
"Banana" → [-0.823, 0.234, -0.456, ..., 0.234]     ← Far from TypeScript!
```

**Why It Matters:**
This lets us search by MEANING instead of keywords. If you stored "I like TypeScript" and search for "What programming languages do I prefer?", the system finds it even though they share no words. The embeddings are similar because the meanings are similar.

**Learn More:**
- Visual explanation: https://jalammar.github.io/illustrated-word2vec/
- Deep dive: https://www.sbert.net/

#### Concept 2: 384 Dimensions

**Simple Explanation:**
A "dimension" is just one number in the list. Our embeddings are lists of 384 numbers. Each number represents a different aspect of meaning:

```python
# Example (simplified to 5 dimensions for clarity)
"TypeScript" → [0.8,  0.3,  -0.1,  0.5,  0.2]
                 ↑     ↑     ↑     ↑     ↑
                 │     │     │     │     └─ "abstractness"
                 │     │     │     └────── "formality"
                 │     │     └─────────── "sentiment"
                 │     └──────────────── "technicality"
                 └───────────────────── "programming-ness"
```

The model learned these dimensions automatically by reading millions of text examples.

**Why It Matters:**
- More dimensions = more nuance captured
- 384 is a sweet spot: enough detail for good accuracy, small enough to be fast
- Fewer dimensions (like 128) would lose nuance
- More dimensions (like 1536) would be slower with minimal accuracy gain for our use case

**Learn More:**
- Dimensionality explained: https://www.pinecone.io/learn/vector-embeddings/

#### Concept 3: Sentence Transformers vs Word Embeddings

**Simple Explanation:**
Early embedding models (like Word2Vec) gave each word its own embedding. To get a sentence embedding, you'd just average the word embeddings. Problem: loses meaning!

Example:
- "The man bit the dog"
- "The dog bit the man"

Word average = same embedding! (same words, different meanings)

Sentence transformers understand word ORDER and CONTEXT. They give different embeddings for these sentences.

**Why It Matters:**
We're storing full sentences and questions, not individual words. We need embeddings that understand complete thoughts.

**Learn More:**
- Sentence-BERT paper: https://arxiv.org/abs/1908.10084

#### Concept 4: Model Caching

**Simple Explanation:**
Loading the 80MB model file into memory takes ~2-3 seconds. If we did this on every request, the server would be slow. Instead, we load it ONCE when the server starts, then reuse that loaded model for all requests.

```python
# ❌ BAD - loads model on every request (slow!)
def generate_embedding(text):
    model = SentenceTransformer('all-MiniLM-L6-v2')  # 2-3 seconds
    return model.encode(text)

# ✅ GOOD - loads model once, reuses forever
_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')  # 2-3 seconds (once)
    return _model

def generate_embedding(text):
    model = get_model()  # Instant (returns cached model)
    return model.encode(text)
```

**Why It Matters:**
- First request: 2-3 seconds (load model)
- All other requests: <1 second (use cached model)
- Memory trade-off: ~500MB RAM to keep model loaded, but worth it for speed

**Learn More:**
- Python global variables: https://realpython.com/python-scope-legb-rule/

## How It Works

### Input
```python
text = "I prefer TypeScript over JavaScript for all my projects"
```

### Process

**Step 1: Lazy-load the model (first call only)**
```python
if self._model is None:
    self._model = SentenceTransformer('all-MiniLM-L6-v2')
```
- Downloads model from HuggingFace Hub (if not already cached)
- Loads 80MB model file into RAM
- Takes 2-3 seconds on first call
- Subsequent calls skip this step

**Step 2: Tokenization**
```
Text: "I prefer TypeScript over JavaScript for all my projects"
         ↓
Tokens: ["I", "prefer", "Type", "##Script", "over", "Java", "##Script",
         "for", "all", "my", "projects"]
```
- Splits text into sub-word tokens
- "##" means it's a continuation of the previous token
- Handles unknown words by breaking them into known pieces

**Step 3: Model processing**
```
Each token → 384-dimensional vector (from model's vocabulary)
     ↓
Pass through 6 BERT layers (neural network)
     ↓
Each layer refines the vectors based on context
     ↓
Final layer: contextual vectors for each token
```
The model learned these transformations by training on billions of words.

**Step 4: Pooling (averaging)**
```
Token vectors:
  "I"          → [0.234, -0.567, ...]
  "prefer"     → [0.123, -0.234, ...]
  "TypeScript" → [0.789, -0.123, ...]
  ...
     ↓
Average all token vectors → One sentence vector
     ↓
[0.456, -0.308, ..., 0.234] (384 numbers)
```

**Step 5: Return**
```python
return embedding.tolist()  # Convert numpy array to Python list
```

### Output
```python
embedding = [0.234, -0.567, 0.123, ..., 0.089]  # 384 floats
```

Each number is typically between -1 and +1, representing strength in that dimension.

## Edge Cases

| Scenario | How We Handle It | Why This Works |
|----------|------------------|----------------|
| **Empty string** | Raise `ValueError` | Better to fail fast than return meaningless embedding |
| **Very long text (>512 words)** | Model truncates to first 512 tokens | BERT models have a context window limit. First 512 tokens usually capture main ideas |
| **Non-English text** | Works reasonably well | Model is multilingual (trained on 50+ languages) |
| **Code snippets** | Embeds successfully | Model has seen code in training data, understands syntax |
| **Special characters** | Tokenizes and embeds | Treats them as regular tokens |
| **Whitespace-only text** | Raise `ValueError` | Same as empty string - catch error early |
| **Multiple calls to same text** | No caching (re-computes) | Computing is fast (<1s), caching would add complexity without much benefit |

## Expected Behavior

### Performance Expectations

- **First call**: 2-3 seconds (model loading + embedding generation)
- **Subsequent calls**: <1 second (just embedding generation)
- **Typical text (50-200 words)**: 100-500ms
- **Short text (<10 words)**: 50-100ms
- **Long text (400-500 words)**: 800ms-1s

### Memory Usage

- **Model in memory**: ~500MB (loaded once, stays resident)
- **Per embedding**: 384 floats × 4 bytes = 1,536 bytes
- **Temporary tensors**: ~50MB during encoding (freed immediately)

### Error Handling

**Validation errors (before processing):**
```python
ValueError: "Cannot generate embedding for empty text"
```

**Model loading errors:**
```python
OSError: "Model not found in cache, attempting download..."
ConnectionError: "Failed to download model from HuggingFace"
```

**Processing errors:**
```python
RuntimeError: "CUDA out of memory" (if GPU enabled but insufficient VRAM)
```

## What You'll Learn

After implementing this component, you should understand:

- [ ] What embeddings are and why they enable semantic search
- [ ] How text gets converted into numbers (tokenization → model → vectors)
- [ ] Why we use pre-trained models instead of building our own
- [ ] What "dimensions" mean in the context of embeddings
- [ ] How to cache expensive resources in Python (lazy loading pattern)
- [ ] The trade-off between model size, speed, and quality
- [ ] Why sentence transformers are better than word embeddings for our use case

## Design Decisions Summary

**Key Decision 1: Use sentence-transformers instead of OpenAI API**
- **Trade-off**: Lower quality embeddings, but free and local
- **Why it's worth it**: Quality is "good enough" for personal use, aligns with constitution

**Key Decision 2: Use all-MiniLM-L6-v2 instead of larger models**
- **Trade-off**: Fewer dimensions (384 vs 768/1024), but 2-3x faster
- **Why it's worth it**: Speed matters for user experience, accuracy difference is minimal for personal use

**Key Decision 3: Lazy-load and cache the model globally**
- **Trade-off**: ~500MB always in RAM, but much faster requests
- **Why it's worth it**: First request is slow, all others are fast. Better UX overall.

**Key Decision 4: No embedding caching (re-compute every time)**
- **Trade-off**: Slight redundancy if same text embedded multiple times
- **Why it's worth it**: Adds complexity (cache invalidation, memory management), generation is fast enough

## Going Deeper

**Next steps to extend your understanding:**

1. **Experiment with different models**: Try `all-mpnet-base-v2` (768 dimensions, higher quality but slower)
2. **Visualize embeddings**: Use dimensionality reduction (t-SNE, UMAP) to plot 384D vectors in 2D
3. **Understand BERT**: Read "The Illustrated BERT" to see how the model works internally
4. **Explore alternatives**: Compare sentence-transformers to OpenAI embeddings, Cohere embeddings

**Resources:**

- **Sentence Transformers docs**: https://www.sbert.net/
- **all-MiniLM-L6-v2 model card**: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- **The Illustrated BERT**: http://jalammar.github.io/illustrated-bert/
- **Embeddings in production**: https://www.pinecone.io/learn/embeddings/

**Optional improvements to consider:**

1. **Batch processing**: Generate multiple embeddings at once for better GPU utilization
2. **GPU acceleration**: Use CUDA if available for 3-5x speedup
3. **Quantization**: Reduce model precision (float32 → float16) for 2x speedup with minimal quality loss
4. **Embedding cache**: Store computed embeddings to avoid re-computation
