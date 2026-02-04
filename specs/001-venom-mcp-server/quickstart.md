# Quickstart Guide: Symbiote MCP Server

**Feature**: Symbiote MCP Server
**Branch**: 001-symbiote-mcp-server
**Date**: 2026-01-31

## Overview

This guide gets you from zero to a working Symbiote MCP server in under 10 minutes. You'll set up the server locally, test it with Claude Desktop, and then deploy it to Azure Container Apps for cross-platform access.

---

## Prerequisites

**Required**:
- Python 3.11 or higher
- Git
- Claude Desktop (for local testing)
- Azure account with free tier (for deployment)
- Docker (for deployment)

**Time Estimate**: 10-15 minutes

---

## Quick Start (Local Development)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/symbiote-mcp.git
cd symbiote-mcp

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (defaults work for local development)
```

**Default `.env` values**:
```bash
PORT=8000
HOST=0.0.0.0
CHROMADB_PATH=./data
EMBEDDING_MODEL=all-MiniLM-L6-v2
COLLECTION_NAME=venom_memories
VENOM_PERSONALITY=default  # Options: default, variant2
```

### Step 3: Run the Server

```bash
# Run with stdio transport (for Claude Desktop)
python src/server.py

# Or run with SSE transport (for remote clients)
uvicorn src.server:app --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Downloading sentence-transformers model (first run only)...
INFO:     Model loaded successfully
INFO:     ChromaDB initialized at ./data
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Test Locally with Claude Desktop

**Configure Claude Desktop**:

1. Open Claude Desktop settings
2. Navigate to "Developer" → "Edit Config"
3. Add Symbiote MCP server:

```json
{
  "mcpServers": {
    "venom": {
      "command": "python",
      "args": ["/absolute/path/to/symbiote-mcp/src/server.py"],
      "env": {
        "CHROMADB_PATH": "/absolute/path/to/symbiote-mcp/data"
      }
    }
  }
}
```

4. Restart Claude Desktop

**Test the connection**:

Open Claude Desktop and try:

```
User: "What prompts do you have available?"
Claude: Should list "venom_identity"

User: "What tools do you have?"
Claude: Should list "search_memory" and "store_memory"

User: "I prefer TypeScript for all my projects"
Venom: *calls store_memory()* "Got it. We're TypeScript all the way."

User: "What languages do I like?"
Venom: *calls search_memory()* "We prefer TypeScript for all projects, remember?"
```

**✅ Success**: If Venom responds using "we" language and references the stored preference, local setup is working!

---

## Deployment to Azure Container Apps

### Step 5: Build Docker Image

```bash
# Build the Docker image
docker build -t symbiote-mcp:latest .

# Test locally (optional)
docker run -p 8000:8000 -v $(pwd)/data:/app/data symbiote-mcp:latest
```

**Test the container**:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "server_name": "symbiote-mcp",
  "version": "1.0.0",
  "embedding_model": "all-MiniLM-L6-v2",
  "collection_name": "venom_memories"
}
```

### Step 6: Deploy to Azure

**Login to Azure**:
```bash
az login
az account set --subscription "Your Subscription Name"
```

**Create resource group**:
```bash
az group create \
  --name symbiote-mcp-rg \
  --location eastus
```

**Create Azure Container Registry (ACR)**:
```bash
az acr create \
  --resource-group symbiote-mcp-rg \
  --name venommcpregistry \
  --sku Basic

# Login to ACR
az acr login --name venommcpregistry
```

**Push Docker image to ACR**:
```bash
# Tag image
docker tag symbiote-mcp:latest venommcpregistry.azurecr.io/symbiote-mcp:latest

# Push to ACR
docker push venommcpregistry.azurecr.io/symbiote-mcp:latest
```

**Create Container Apps environment**:
```bash
az containerapp env create \
  --name symbiote-mcp-env \
  --resource-group symbiote-mcp-rg \
  --location eastus
```

**Create persistent storage**:
```bash
az containerapp env storage set \
  --name symbiote-mcp-env \
  --resource-group symbiote-mcp-rg \
  --storage-name venom-data \
  --azure-file-account-name <storage-account-name> \
  --azure-file-account-key <storage-account-key> \
  --azure-file-share-name venom-memories \
  --access-mode ReadWrite
```

**Deploy Container App**:
```bash
az containerapp create \
  --name symbiote-mcp \
  --resource-group symbiote-mcp-rg \
  --environment symbiote-mcp-env \
  --image venommcpregistry.azurecr.io/symbiote-mcp:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server venommcpregistry.azurecr.io \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 1 \
  --env-vars \
    PORT=8000 \
    HOST=0.0.0.0 \
    CHROMADB_PATH=/app/data \
    EMBEDDING_MODEL=all-MiniLM-L6-v2 \
    COLLECTION_NAME=venom_memories
```

**Get the public URL**:
```bash
az containerapp show \
  --name symbiote-mcp \
  --resource-group symbiote-mcp-rg \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

**Expected output**: `symbiote-mcp.kindsky-12345678.eastus.azurecontainerapps.io`

### Step 7: Connect from Claude Web/Mobile

**Configure Claude.ai**:

1. Open https://claude.ai
2. Go to Settings → Integrations → MCP Servers
3. Add new server:
   - **Name**: Venom
   - **URL**: `https://symbiote-mcp.kindsky-12345678.eastus.azurecontainerapps.io/mcp`
   - **Transport**: SSE

4. Save and verify connection

**Test cross-platform**:

1. **On Claude Web**: "I'm working on a React authentication module"
   - Venom stores this in memory

2. **On Claude Mobile** (2 hours later): "What am I building?"
   - Venom retrieves and references the React auth module

3. **On ChatGPT** (with MCP plugin): Same memory accessible!

**✅ Success**: If memories persist across platforms and sessions, deployment is working!

---

## Verification Checklist

After completing the quickstart, verify:

- [ ] Local server starts without errors
- [ ] Health check endpoint returns `{"status": "healthy"}`
- [ ] Claude Desktop connects and lists prompts/tools
- [ ] `venom_identity` prompt loads personality from file
- [ ] `store_memory` successfully stores information
- [ ] `search_memory` retrieves stored memories with relevance scores
- [ ] Venom uses "we" language in responses
- [ ] Memories persist after restarting server
- [ ] Azure deployment completes successfully
- [ ] Container scales to zero when idle
- [ ] Container wakes up in <2 seconds on new request
- [ ] Same memories accessible from web and mobile

---

## Testing Personality Variants

Venom supports multiple personality variants for experimentation. You can easily switch between them to find which works best.

### Available Personality Variants

1. **default** - Original Venom personality from `venom_personality.md`
2. **variant2** - Alternative personality from `venom_personality_v2.md`

### How to Switch Personalities

**Method 1: Environment Variable**
```bash
# Test default personality
VENOM_PERSONALITY=default python src/server.py

# Test alternative personality
VENOM_PERSONALITY=variant2 python src/server.py
```

**Method 2: Update .env file**
```bash
# Edit .env
echo "VENOM_PERSONALITY=variant2" >> .env

# Restart server
python src/server.py
```

### Verifying Active Personality

Check which personality is loaded:
```bash
curl http://localhost:8000/health | jq '.personality_variant'
```

Expected output: `"variant2"` or `"default"`

### Comparing Personalities

**Test protocol for A/B comparison**:

1. **Record test interactions**:
   ```
   - "Should I refactor this code?"
   - "Help me write a function"
   - "What are we working on?"
   ```

2. **Test with default**:
   ```bash
   VENOM_PERSONALITY=default python src/server.py
   # Run all test interactions, record responses
   ```

3. **Test with variant2**:
   ```bash
   VENOM_PERSONALITY=variant2 python src/server.py
   # Run same test interactions, record responses
   ```

4. **Compare**:
   - Tone and wit level
   - Use of "we" language
   - Helpfulness vs. sarcasm balance
   - Symbiote metaphor usage

5. **Decide**: Choose the variant that provides the best user experience

**Note**: You need to restart the server to switch personalities. Memories persist across personality changes (they use the same ChromaDB collection).

---

## Common Issues & Solutions

### Issue: "Model not found" error

**Symptom**: Error during startup about missing model

**Solution**:
```bash
# Pre-download the model manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Issue: ChromaDB permission denied

**Symptom**: Cannot write to `/app/data`

**Solution**:
```bash
# Ensure data directory exists and is writable
mkdir -p ./data
chmod 755 ./data
```

### Issue: Claude Desktop can't connect

**Symptom**: MCP server not appearing in Claude Desktop

**Solution**:
1. Check config file path is absolute (not relative)
2. Verify Python path is correct
3. Check server.py has execute permissions
4. Restart Claude Desktop after config changes

### Issue: Container fails to start on Azure

**Symptom**: Container restarts repeatedly

**Solution**:
```bash
# Check container logs
az containerapp logs show \
  --name symbiote-mcp \
  --resource-group symbiote-mcp-rg

# Common fixes:
# - Verify persistent volume is mounted correctly
# - Check environment variables are set
# - Ensure port 8000 is exposed
```

### Issue: Memory search returns no results

**Symptom**: `search_memory` returns empty array even with stored memories

**Solution**:
1. Verify memories were actually stored (check ChromaDB data directory)
2. Try broader search queries
3. Check relevance threshold (default filters out <30%)
4. Verify embeddings are being generated correctly

---

## Next Steps

**After successful quickstart**:

1. **Read the learning docs**: `docs/learning/00-overview.md` explains how everything works
2. **Explore personality**: Edit `venom_personality.md` to customize Venom's behavior
3. **Test edge cases**: Try empty queries, very long content, concurrent requests
4. **Monitor costs**: Check Azure billing dashboard (should be $0 in free tier)
5. **Extend functionality**: Review `docs/learning/` for understanding internals before modifying

---

## Quick Reference

**Start local server**:
```bash
python src/server.py
# or with specific personality
VENOM_PERSONALITY=variant2 python src/server.py
```

**Check health** (includes personality variant):
```bash
curl http://localhost:8000/health
```

**View logs** (Azure):
```bash
az containerapp logs show --name symbiote-mcp --resource-group symbiote-mcp-rg --follow
```

**Update deployment** (after code changes):
```bash
docker build -t symbiote-mcp:latest .
docker tag symbiote-mcp:latest venommcpregistry.azurecr.io/symbiote-mcp:latest
docker push venommcpregistry.azurecr.io/symbiote-mcp:latest
az containerapp update --name symbiote-mcp --resource-group symbiote-mcp-rg --image venommcpregistry.azurecr.io/symbiote-mcp:latest
```

**Stop/Start Azure app**:
```bash
# Stop (scale to 0)
az containerapp update --name symbiote-mcp --resource-group symbiote-mcp-rg --min-replicas 0 --max-replicas 0

# Start (restore scaling)
az containerapp update --name symbiote-mcp --resource-group symbiote-mcp-rg --min-replicas 0 --max-replicas 1
```

---

## Support & Documentation

- **Full Spec**: `specs/001-symbiote-mcp-server/spec.md`
- **Architecture**: `specs/001-symbiote-mcp-server/plan.md`
- **Data Model**: `specs/001-symbiote-mcp-server/data-model.md`
- **API Contracts**: `specs/001-symbiote-mcp-server/contracts/mcp-schema.json`
- **Learning Docs**: `docs/learning/` (educational walkthroughs)
- **Constitution**: `.specify/memory/constitution.md` (design principles)

---

**You're now ready to use Venom as your cross-platform AI symbiote! 🕷️**
