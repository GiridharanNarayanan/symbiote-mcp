# Research: Symbiote MCP Server Technology Choices

**Feature**: Symbiote MCP Server
**Branch**: 001-symbiote-mcp-server
**Date**: 2026-01-31

## Overview

This document consolidates research findings and rationale for all technology choices in the Symbiote MCP Server implementation. No unknowns or clarifications were needed as all technologies are well-established and align with constitutional requirements.

## Technology Decisions

### 1. MCP Protocol Implementation

**Decision**: Use official `mcp` Python SDK with FastAPI for SSE transport

**Rationale**:
- Official SDK ensures compliance with MCP specification
- FastAPI provides native async/await support and SSE capabilities
- Proven combination for remote MCP servers
- Aligns with constitution's requirement for remote (not stdio) architecture

**Alternatives Considered**:
- **Custom MCP implementation**: Rejected due to complexity and maintenance burden
- **Flask with Flask-SSE**: Rejected because FastAPI has better async support and modern Python typing
- **Stdio-only transport**: Rejected because it doesn't support mobile platforms (critical requirement)

**Best Practices**:
- Use FastAPI's EventSourceResponse for SSE endpoints
- Implement proper health check endpoints for container orchestration
- Support both stdio (development) and SSE (production) transports

---

### 2. Vector Embeddings

**Decision**: sentence-transformers library with `all-MiniLM-L6-v2` model

**Rationale**:
- Free and runs locally (no API costs, no rate limits)
- 384-dimension vectors provide good semantic representation
- Fast enough for personal use (<1s embedding generation)
- Industry-standard library with strong community support
- Model size (80MB) is reasonable for container deployment

**Alternatives Considered**:
- **OpenAI Embeddings API**: Rejected due to cost ($0.0001/1K tokens) and constitution's "no paid APIs" rule
- **Word2Vec**: Rejected because it's less accurate for sentences (designed for words)
- **Larger BERT models**: Rejected due to slower performance and larger size without proportional accuracy gains for personal use
- **Custom model fine-tuning**: Rejected as overkill for personal use and requires ML expertise

**Best Practices**:
- Cache model globally in memory (load once, use many times)
- Pre-download model during Docker build (not at runtime)
- Use default model settings for consistency
- Handle long text truncation gracefully (512 token limit)

---

### 3. Vector Database

**Decision**: ChromaDB embedded mode with local file storage

**Rationale**:
- No separate database server required (simplicity)
- File-based persistence via persistent volumes
- Native cosine similarity search built-in
- Python-first design integrates seamlessly
- Good enough performance for personal scale (<1000 memories)
- Zero operational overhead

**Alternatives Considered**:
- **Pinecone/Weaviate cloud**: Rejected due to cost and constitution's "no paid APIs" rule
- **PostgreSQL with pgvector**: Rejected due to additional complexity of managing PostgreSQL server
- **Redis with RediSearch**: Rejected due to additional service dependency
- **ChromaDB client-server mode**: Rejected because embedded mode is simpler and sufficient for single-user

**Best Practices**:
- Use persistent volume mount for `/app/data` in production
- Single collection named `venom_memories`
- Include metadata (timestamp, tags) with each embedding
- Use cosine similarity for semantic search
- Return relevance scores as percentages for user clarity

---

### 4. Web Framework

**Decision**: FastAPI with Uvicorn ASGI server

**Rationale**:
- Native async/await support (required by constitution)
- Built-in SSE support via EventSourceResponse
- Excellent type hint integration (required by constitution)
- Fast performance suitable for low-latency requirements
- Modern, actively maintained framework
- Built-in OpenAPI documentation (useful for debugging)

**Alternatives Considered**:
- **Flask**: Rejected due to weaker async support and older design
- **Django**: Rejected as overkill for a simple API server
- **aiohttp**: Rejected because FastAPI provides better developer experience
- **Pure ASGI**: Rejected due to unnecessary low-level complexity

**Best Practices**:
- Use Uvicorn with HTTP/2 support for SSE
- Implement health check endpoints (`/`, `/health`)
- Use FastAPI's dependency injection for shared resources
- Leverage async route handlers throughout
- Use Pydantic models for request/response validation

---

### 5. Deployment Platform

**Decision**: Azure Container Apps with Docker containerization

**Rationale**:
- Scale-to-zero saves costs (stays in free tier)
- Better cold start performance than Azure Functions (<10s vs 30s+)
- Managed container orchestration (simpler than VMs)
- Native persistent volume support for ChromaDB data
- HTTP/2 support for SSE transport
- Free tier: 180,000 vCPU-seconds/month (sufficient for 20-50 interactions/day)

**Alternatives Considered**:
- **Azure Functions**: Rejected due to slower cold starts and less control over environment
- **Azure VMs**: Rejected due to higher cost and management overhead
- **Azure Kubernetes Service (AKS)**: Rejected as overkill for single container
- **AWS Fargate/Lambda**: Rejected to stay within one cloud provider
- **Heroku**: Rejected due to higher cost beyond free tier

**Best Practices**:
- Configure scale-to-zero with minimum 0 replicas
- Set resource limits: 0.5 CPU, 1GB memory
- Mount persistent volume to `/app/data`
- Use multi-stage Docker builds for smaller images
- Pre-download embedding model during build

---

### 6. Configuration Management

**Decision**: Environment variables with Python `os.environ` and defaults

**Rationale**:
- Standard 12-factor app pattern
- Azure Container Apps native support
- Simple and explicit (no complex config libraries needed)
- Easy to override for different environments

**Alternatives Considered**:
- **YAML/JSON config files**: Rejected due to unnecessary complexity for small config surface
- **python-decouple or similar**: Rejected as unnecessary abstraction
- **Azure Key Vault**: Rejected because no secrets needed (public endpoint for personal use)

**Best Practices**:
- Provide `.env.example` for local development
- Use sensible defaults in code
- Validate required env vars on startup
- Document all env vars in README

---

### 7. Development & Testing

**Decision**: Manual testing only, no automated tests in Phase 1

**Rationale**:
- Constitution explicitly states "manual testing only"
- Faster initial development
- Automated tests deferred to future phase
- Focus on core functionality first

**Alternatives Considered**:
- **pytest with automated tests**: Deferred to Phase 2 per constitution
- **Integration tests**: Deferred to Phase 2
- **Load testing**: Not needed for personal use scale

**Best Practices**:
- Document manual test scenarios in `tests/manual_testing.md`
- Test locally with Claude Desktop (stdio transport)
- Test remotely with deployed server (SSE transport)
- Verify memory persistence through container restarts

---

## Integration Patterns

### MCP Protocol Flow
```
Client (Claude/ChatGPT) → SSE Connection (/mcp endpoint)
                        → MCP Request (list_prompts/list_tools/call_tool)
                        → Server Handler
                        → Response via SSE
```

### Memory Storage Flow
```
User message → store_memory tool called
            → Generate embedding (sentence-transformers)
            → Store in ChromaDB (content + embedding + metadata)
            → Return confirmation with memory ID
```

### Memory Search Flow
```
User message → search_memory tool called
            → Generate query embedding (sentence-transformers)
            → ChromaDB cosine similarity search
            → Filter results (relevance >30%)
            → Return top N results with scores
```

### Personality Injection Flow
```
Client requests prompts → venom_identity prompt
                       → Read venom_personality.md file
                       → Return content as system prompt
                       → Client injects into LLM context
```

---

## Personality Experimentation

### Decision: Environment Variable Variant Switching

**Decision**: Support multiple personality files selectable via `VENOM_PERSONALITY` environment variable

**Rationale**:
- Enables A/B testing different personality styles
- Zero code changes needed to switch personalities
- Maintains simplicity (single env var, file-based)
- No API surface changes (still one `venom_identity` prompt)
- Requires server restart to switch (aligns with stateless design)

**Alternatives Considered**:
- **Multiple prompt names** (venom_identity_v1, venom_identity_v2): Rejected because requires manual client-side prompt selection every session
- **Two separate MCP servers**: Rejected due to resource duplication and separate memory databases
- **Dynamic runtime switching**: Rejected as unnecessary complexity for experimentation use case

**Best Practices**:
- Default to `"default"` variant when env var not set
- Fall back to default if invalid variant specified
- Log which personality variant is loaded on startup
- Include personality variant in health check response

**Implementation**:
```python
# In src/prompts/venom.py
personality_files = {
    "default": "venom_personality.md",
    "variant2": "venom_personality_v2.md",
}
variant = os.getenv("VENOM_PERSONALITY", "default")
file_path = personality_files.get(variant, "venom_personality.md")
```

**Testing Strategy**:
1. Run server with default personality, test interactions
2. Stop server, set `VENOM_PERSONALITY=variant2`, restart
3. Test same interactions, compare responses
4. Evaluate which personality performs better for user experience

---

## Key Dependencies & Versions

**Core Dependencies**:
- `mcp` - Official MCP Python SDK
- `fastapi` - Web framework (latest stable)
- `uvicorn[standard]` - ASGI server with HTTP/2
- `sentence-transformers` - Embeddings library
- `chromadb` - Vector database
- `python-dotenv` - Local development env loading

**Python Version**: 3.11+ (for modern async/await and type hints)

**Docker Base Image**: `python:3.11-slim` (balance between size and functionality)

---

## Performance Considerations

### Optimization Strategies

1. **Model Caching**: Load sentence-transformers model once globally, reuse across requests
2. **Pre-download Model**: Include model in Docker image to avoid runtime downloads
3. **Async All The Way**: Use async/await for all I/O operations (file reads, database queries)
4. **Efficient Embeddings**: Use smallest model that meets quality requirements (384 dims vs 768/1024)
5. **ChromaDB Embedded**: Avoid network overhead of separate database server

### Expected Performance

Based on typical hardware (0.5 CPU, 1GB RAM):
- Embedding generation: 100-500ms for typical text (50-200 words)
- ChromaDB search: 50-200ms for <1000 memories
- Total search_memory latency: 200-500ms ✅ Meets <500ms requirement
- Total store_memory latency: 200-700ms ✅ Meets <1s requirement

---

## Security Considerations

**Approach**: Public endpoint for personal use (no authentication)

**Rationale**:
- Single user context (constitution explicit)
- Deploying for personal use only
- Trust Azure infrastructure security
- Adds complexity without proportional benefit for solo use

**Future Enhancements** (out of scope for Phase 1):
- API key authentication if sharing with others
- Memory encryption at rest
- Rate limiting if usage patterns change

---

## Cost Analysis

### Azure Container Apps Free Tier

**Limits**:
- 180,000 vCPU-seconds/month
- 360,000 GiB-seconds/month
- 2M requests/month

**Expected Usage** (20-50 interactions/day):
- Daily: ~30 interactions × 2s average = 60 vCPU-seconds
- Monthly: 60 × 30 = 1,800 vCPU-seconds
- **Utilization**: 1% of free tier ✅ Well within limits

**Expected Cost**: $0/month (stays in free tier)

---

## Conclusion

All technology choices:
1. ✅ Align with constitutional requirements
2. ✅ Meet performance targets
3. ✅ Stay within cost constraints
4. ✅ Provide educational value
5. ✅ Prioritize simplicity
6. ✅ Use proven, maintained technologies

No further research required. Ready to proceed to Phase 1 (Design & Contracts).
