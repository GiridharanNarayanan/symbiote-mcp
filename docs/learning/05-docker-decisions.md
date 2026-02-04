# Docker Containerization - Decisions Log

## Decision 1: python:3.11-slim vs python:3.11

**Context:** Choose base image.

**Decision:** python:3.11-slim

**Reasoning:**
- 70% smaller (120MB vs 400MB)
- Has everything we need
- Faster to download and deploy

**Trade-offs:**
- ✅ Gained: Smaller image, faster deployment
- ❌ Lost: Some packages missing (but we don't need them)

## Decision 2: Pre-download Model vs Download at Runtime

**Context:** When to download 80MB embedding model?

**Decision:** Pre-download during Docker build

**Reasoning:**
- Startup must be <10s (downloading takes 30s)
- Production containers might not have internet
- Image size increase (80MB) acceptable

**Trade-offs:**
- ✅ Gained: Fast startup, offline capability
- ❌ Lost: 80MB image size (acceptable)

## Decision 3: CMD vs ENTRYPOINT

**Context:** How to specify container command?

**Decision:** CMD ["python", "-m", "src.server"]

**Reasoning:**
- CMD is easier to override at runtime
- Can pass --stdio flag if needed
- ENTRYPOINT would require --entrypoint override

**Trade-offs:**
- ✅ Gained: Flexibility
- ❌ Lost: Nothing (CMD works perfectly)

## Problem 1: Slow Builds

**What Happened:** Every code change triggers full rebuild (30+ seconds)

**Why:** Requirements installation in same layer as code copy

**Solution:** Copy requirements.txt first, then code:
```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt  # Cached unless requirements change
COPY src/ /app/src/                   # Only this layer rebuilds on code change
```

**Lesson:** Put stable layers before changing layers for better caching
