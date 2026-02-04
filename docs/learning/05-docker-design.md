# Docker Containerization - Design

## What We're Building

A multi-stage Docker image that packages the Venom MCP server with all dependencies, pre-downloads the embedding model, and runs efficiently in production with minimal size and fast startup.

**Location:** `Dockerfile`, `.dockerignore`

**Result:** Docker image (~500MB) ready for Azure Container Apps deployment

## Architecture Diagram

```
Dockerfile (Multi-stage Build)
  │
  ├─► Stage 1: model-builder
  │   - Base: python:3.11-slim
  │   - Install sentence-transformers
  │   - Download all-MiniLM-L6-v2 model (80MB)
  │   - Cache at /root/.cache/torch/
  │
  └─► Stage 2: production
      - Base: python:3.11-slim
      - Install system dependencies (gcc, g++)
      - Copy requirements.txt
      - Install Python packages
      - Copy pre-downloaded model from Stage 1
      - Copy application code
      - Copy personality files
      - Create /app/data directory
      - EXPOSE 8000
      - CMD python -m src.server
```

## Why This Design?

### Technology Choice: Multi-stage Build

**Alternatives Considered:**

1. **Single-stage build**
   - **Pros:** Simpler Dockerfile
   - **Cons:** Larger image (includes build tools), slower startup (downloads model at runtime)
   - **Why rejected:** Wastes space, runtime downloads fail without internet

2. **Pre-built image with model**
   - **Pros:** Fastest startup, no build step
   - **Cons:** Can't customize, vendor lock-in
   - **Why rejected:** Need to own the build process

3. **Multi-stage build (chosen)**
   - **Pros:** Small final image, model pre-downloaded, fast startup
   - **Cons:** Slightly more complex Dockerfile
   - **Why chosen:** Best balance of size and speed

### Key Concepts

#### Concept 1: Docker Images vs Containers

**Simple Explanation:**
- **Image**: Recipe/template (like a class in programming)
- **Container**: Running instance (like an object)

```
Image: Venom MCP Server v1.0 (blueprint)
  ↓
Container 1: Running on localhost:8000
Container 2: Running on Azure at venom-mcp.azurecontainerapps.io
```

#### Concept 2: Multi-stage Builds

**Simple Explanation:**
Use multiple FROM statements. Early stages build/download things. Final stage copies only what's needed.

```
Stage 1 (builder):
  - Install build tools (200MB)
  - Compile dependencies
  - Download model (80MB)
  - Total: 500MB

Stage 2 (production):
  - Copy compiled deps from Stage 1
  - Copy model from Stage 1
  - No build tools
  - Total: 250MB (saved 250MB!)
```

#### Concept 3: Layer Caching

**Simple Explanation:**
Docker caches each step. If nothing changed, reuses cache.

```
RUN pip install requirements.txt  ← Cached if requirements.txt unchanged
COPY src/ /app/src/                ← Runs if src/ changed
```

Order matters: Put stable things first (requirements), changing things last (code).

#### Concept 4: .dockerignore

**Simple Explanation:**
Like .gitignore but for Docker. Files matching patterns aren't copied into image.

```
.dockerignore:
  __pycache__/  ← Don't copy Python cache
  .git/         ← Don't copy git history
  data/         ← Don't copy local data

Result: Smaller context, faster builds
```

## How It Works

### Build Process

**Command:**
```bash
docker build -t venom-mcp:latest .
```

**Steps:**
1. **Stage 1: Download model**
   - Start from python:3.11-slim
   - `pip install sentence-transformers`
   - Run Python script to download model
   - Model saved to `/root/.cache/torch/`

2. **Stage 2: Production image**
   - Start fresh from python:3.11-slim
   - Install system packages (gcc for compilations)
   - Copy requirements.txt (triggers cache if unchanged)
   - `pip install -r requirements.txt`
   - Copy model from Stage 1
   - Copy application code
   - Set environment variables
   - Define CMD

### Run Container

**Command:**
```bash
docker run -p 8000:8000 -v $(pwd)/data:/app/data venom-mcp:latest
```

**Breakdown:**
- `-p 8000:8000`: Map container port 8000 to host port 8000
- `-v $(pwd)/data:/app/data`: Mount host directory as persistent volume
- `venom-mcp:latest`: Image to run

## Edge Cases

| Scenario | How We Handle It |
|----------|------------------|
| **Model download fails** | Build fails (better than runtime failure) |
| **Requirements change** | Cache invalidated, rebuild from that layer |
| **Port 8000 in use** | Container fails to start (clear error) |
| **No persistent volume** | Data lost on restart (document requirement) |

## What You'll Learn

- [ ] What Docker images and containers are
- [ ] Why multi-stage builds reduce image size
- [ ] How layer caching speeds up rebuilds
- [ ] The role of .dockerignore in efficient builds
- [ ] How to pre-download dependencies in Docker
- [ ] Why persistent volumes are needed for data
- [ ] The difference between CMD and ENTRYPOINT

## Design Decisions

**Key Decision 1:** Multi-stage vs single-stage
- **Trade-off:** More complex, but 50% smaller image
- **Why:** Size matters for deployment speed

**Key Decision 2:** Pre-download model in build
- **Trade-off:** Larger image, but faster startup and offline capability
- **Why:** Cold start must be <10s requirement

**Key Decision 3:** Slim base image vs full
- **Trade-off:** Smaller (fewer packages), but might miss dependencies
- **Why:** Tested and works, 70% size reduction vs full image
