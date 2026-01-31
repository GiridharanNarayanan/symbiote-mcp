# Multi-stage build for Venom MCP Server
# Stage 1: Download embedding model
FROM python:3.11-slim as model-builder

WORKDIR /models

# Install sentence-transformers to download model
RUN pip install --no-cache-dir sentence-transformers

# Download the embedding model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Stage 2: Production image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy pre-downloaded model from builder stage
COPY --from=model-builder /root/.cache/torch/sentence_transformers /root/.cache/torch/sentence_transformers

# Copy application code
COPY src/ /app/src/
COPY venom_personality.md /app/
COPY venom_personality_v2.md /app/

# Create data directory for ChromaDB
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Environment variables (can be overridden at runtime)
ENV PORT=8000
ENV HOST=0.0.0.0
ENV CHROMADB_PATH=/app/data
ENV EMBEDDING_MODEL=all-MiniLM-L6-v2
ENV COLLECTION_NAME=venom_memories
ENV VENOM_PERSONALITY=default

# Run the server
CMD ["python", "-m", "src.server"]
