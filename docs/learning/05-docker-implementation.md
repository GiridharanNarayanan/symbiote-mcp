# Docker Containerization - Implementation

## Code Overview

**File:** `Dockerfile`
**Lines:** ~40
**Base Images:** python:3.11-slim (both stages)

## Key Sections

### Stage 1: Model Builder

```dockerfile
FROM python:3.11-slim as model-builder

WORKDIR /models

RUN pip install --no-cache-dir sentence-transformers

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

**What This Does:**
- Creates temporary stage for downloading model
- Installs sentence-transformers
- Downloads model to cache directory
- This stage is discarded in final image

**Line-by-Line:**
- `FROM ... as model-builder`: Named stage for copying later
- `WORKDIR /models`: Set working directory
- `--no-cache-dir`: Don't save pip cache (smaller layer)
- Python one-liner: Download and cache model

### Stage 2: Production Image

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy model from builder stage
COPY --from=model-builder /root/.cache/torch/sentence_transformers /root/.cache/torch/sentence_transformers

# Copy application code
COPY src/ /app/src/
COPY venom_personality.md /app/
COPY venom_personality_v2.md /app/

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Environment variables
ENV PORT=8000
ENV HOST=0.0.0.0

# Run server
CMD ["python", "-m", "src.server"]
```

**What This Does:**
Complete production image with all code, dependencies, and pre-downloaded model.

**Key Parts:**
- System deps: gcc/g++ needed for compiling some Python packages
- `rm -rf /var/lib/apt/lists/*`: Clean up apt cache (smaller image)
- Copy requirements first: Leverage layer cache
- `COPY --from=model-builder`: Get model from Stage 1
- `mkdir -p /app/data`: Create directory for ChromaDB
- `EXPOSE 8000`: Document port (doesn't actually publish)
- `ENV`: Default environment variables (can override at runtime)
- `CMD`: Command to run when container starts

## .dockerignore

```
.git/
__pycache__/
*.pyc
.venv/
venv/
.env
data/
docs/
tests/
.DS_Store
```

**What This Does:**
Excludes files from Docker build context (faster builds, smaller context).

## Key Takeaways

1. **Multi-stage builds save space**: Final image doesn't include build tools
2. **Pre-download in build, not runtime**: Model available offline
3. **Layer order matters**: Stable layers first (requirements), changing layers last (code)
4. **Clean up in same layer**: `apt-get update && install && rm` in one RUN
5. **.dockerignore is critical**: Prevents copying unnecessary files
