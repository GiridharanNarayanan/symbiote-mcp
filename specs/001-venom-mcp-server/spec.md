# Feature Specification: Symbiote MCP Server

**Feature Branch**: `001-symbiote-mcp-server`
**Created**: 2026-01-25
**Status**: Draft
**Input**: User description: "Build Venom, a cross-platform AI assistant with persistent memory using Model Context Protocol (MCP)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cross-Platform Memory Access (Priority: P1) 🎯 MVP

One continuous AI consciousness accessible from any MCP-compatible platform (Claude, ChatGPT, VS Code) with shared semantic memory that persists across sessions and platforms.

**Why this priority**: This is the core value proposition. Without cross-platform memory access, Venom is just another chatbot. This enables the "one consciousness" experience that defines the product.

**Independent Test**: Can be fully tested by adding the MCP server URL to Claude.ai settings, storing a memory on mobile, and retrieving it on desktop. Delivers immediate value as a working cross-platform memory system.

**Acceptance Scenarios**:

1. **Given** a deployed Symbiote MCP server, **When** user adds the server URL to Claude.ai settings, **Then** connection is verified, venom_identity prompt is available, and both memory tools are accessible
2. **Given** Venom is connected to Claude mobile, **When** user shares a preference "I prefer TypeScript over JavaScript", **Then** Venom calls store_memory() and confirms storage
3. **Given** a memory was stored on Claude mobile, **When** user asks ChatGPT desktop 2 hours later "Help me write a script", **Then** Venom calls search_memory(), retrieves the TypeScript preference, and uses it without re-explanation
4. **Given** multiple platforms connected, **When** user switches between web/mobile/desktop, **Then** same memories are available everywhere with zero per-platform configuration

---

### User Story 2 - Semantic Memory Search & Storage (Priority: P1) 🎯 MVP

Store and retrieve memories using meaning-based search rather than keyword matching, enabling contextually relevant memory retrieval that understands intent.

**Why this priority**: Semantic search is what makes the memory system intelligent. Keyword search would require exact phrase matches, making the system frustrating. This is essential for MVP viability.

**Independent Test**: Store "I love building web apps with React" and search for "frontend development preferences" - should retrieve the React preference even without exact keyword match. Delivers intelligent context retrieval.

**Acceptance Scenarios**:

1. **Given** an empty memory database, **When** user shares "I'm working on a React app with TypeScript and authentication", **Then** Venom stores this with appropriate tags (project, preference) and generates a 384-dimension embedding
2. **Given** stored memories exist, **When** user asks "what am I building?", **Then** search_memory() returns top 5 most semantically relevant results ordered by similarity score
3. **Given** a search query, **When** results are returned, **Then** each result includes content, timestamp, relevance percentage (0-100%), and low-relevance results (<30%) are filtered out
4. **Given** stored memories, **When** container restarts, **Then** all memories persist via ChromaDB persistent volume and are immediately accessible

---

### User Story 3 - Mandatory Memory Protocol (Priority: P1) 🎯 MVP

Venom automatically checks memory before every response without user prompting, ensuring continuous context awareness and eliminating the need for "remember this" or "check your memory" commands.

**Why this priority**: This is what differentiates Venom from standard chatbots with optional memory. The mandatory protocol ensures the symbiote experience feels natural and automatic.

**Independent Test**: Start fresh conversation, share a preference, then start new conversation without mentioning it - Venom should proactively search memory and reference the preference. Delivers the "continuous consciousness" experience.

**Acceptance Scenarios**:

1. **Given** venom_identity prompt loaded, **When** user sends any message, **Then** Venom MUST call search_memory() as Step 1 before generating response
2. **Given** no memories exist yet, **When** user asks first question, **Then** search returns empty results gracefully and Venom responds normally
3. **Given** relevant memories exist, **When** Venom searches and finds context, **Then** response incorporates memories naturally without explicitly saying "I found in memory that..."
4. **Given** user shares new important information, **When** Venom determines it's worth storing, **Then** store_memory() is called proactively without user saying "remember this"

---

### User Story 4 - Consistent Symbiote Personality (Priority: P2)

Venom maintains consistent personality across all platforms: always uses "we" language, sarcastic/witty tone, symbiote metaphor, and protective loyalty as defined in venom_personality.md.

**Why this priority**: Personality consistency completes the "one consciousness" illusion. While memory (P1) ensures factual continuity, personality ensures emotional continuity. This is secondary to core functionality but essential for user experience.

**Independent Test**: Ask the same question on Claude and ChatGPT - tone, language style, and symbiote references should be identical. Delivers personality cohesion across platforms.

**Acceptance Scenarios**:

1. **Given** venom_identity prompt loaded from venom_personality.md, **When** user interacts on any platform, **Then** Venom ALWAYS uses "we" instead of "I" (e.g., "We should refactor this" not "I think you should")
2. **Given** user asks a question on Claude web, **When** same question asked on ChatGPT mobile, **Then** tone, wit level, and symbiote references are consistent
3. **Given** user makes a mistake, **When** Venom responds, **Then** response includes gentle sarcasm with protective undertone (never mean, always helpful)
4. **Given** any interaction, **When** Venom references itself, **Then** uses symbiote metaphor ("we're bonded", "our memories", "we work together")

---

### User Story 5 - Personality Experimentation (Priority: P2)

Support testing multiple personality variants to determine which works best, using environment variable switching without code changes or server modifications.

**Why this priority**: Allows iterative refinement of Venom's personality based on real usage. Essential for finding the optimal balance of wit, helpfulness, and symbiote metaphor. Secondary to core memory functionality but important for user experience optimization.

**Independent Test**: Run server with VENOM_PERSONALITY=default, test interactions, restart with VENOM_PERSONALITY=variant2, compare behavior. Delivers easy A/B testing capability.

**Acceptance Scenarios**:

1. **Given** multiple personality files exist (venom_personality.md, venom_personality_v2.md), **When** VENOM_PERSONALITY env var is set to "variant2", **Then** server loads venom_personality_v2.md instead of default
2. **Given** server running with personality variant, **When** health check endpoint is queried, **Then** response includes which personality variant is active
3. **Given** no VENOM_PERSONALITY env var set, **When** server starts, **Then** defaults to "default" variant (venom_personality.md)
4. **Given** invalid personality variant specified, **When** server starts, **Then** falls back to default variant and logs warning

---

### User Story 6 - Zero-Cost Deployment & Operation (Priority: P3)

Deploy to Azure Container Apps with scale-to-zero capability, staying within free tier limits while maintaining acceptable performance for personal use.

**Why this priority**: Cost efficiency enables sustainability but doesn't affect core functionality. Can be tested/developed locally first, then deployed. Important for long-term viability but not blocking for MVP testing.

**Independent Test**: Deploy to Azure, monitor usage for 1 month of normal personal use, verify costs remain $0-2/month. Delivers sustainable operation.

**Acceptance Scenarios**:

1. **Given** containerized application, **When** deployed to Azure Container Apps, **Then** uses 0.5 CPU cores max, 1GB memory max, 2GB persistent volume
2. **Given** no active requests, **When** system is idle for configured period, **Then** scales to zero replicas automatically
3. **Given** scaled to zero, **When** new MCP request arrives, **Then** container wakes in <2s and responds in <10s total
4. **Given** 1 month of typical personal use (20-50 interactions/day), **When** Azure billing calculated, **Then** stays within free tier (180,000 vCPU-seconds/month) and costs $0-2

---

### Edge Cases

- **What happens when** ChromaDB data directory is empty on first startup?
  - System initializes empty collection, handles gracefully, first memories create the collection

- **What happens when** search query is empty string or whitespace?
  - Return validation error, don't attempt embedding generation

- **What happens when** user stores extremely long content (>10,000 characters)?
  - Accept and process (sentence-transformers handles long text), but may be slower than 1s target

- **What happens when** ChromaDB persistent volume is full?
  - Log storage error, return error to client, don't crash server

- **What happens when** sentence-transformers model download fails during Docker build?
  - Build fails with clear error message, requires retry

- **What happens when** multiple MCP clients connect simultaneously?
  - FastAPI handles concurrently (async), ChromaDB handles thread-safe reads/writes

- **What happens when** search returns zero results?
  - Return empty results array gracefully, Venom responds without memory context

- **What happens when** Azure Container Apps instance is replaced (deployment update)?
  - Persistent volume preserves data, new instance reconnects to same storage, zero data loss

## Requirements *(mandatory)*

### Functional Requirements

#### MCP Protocol
- **FR-001**: System MUST expose MCP protocol via SSE endpoint at `/mcp` supporting long-lived connections
- **FR-002**: System MUST expose `venom_identity` prompt loading content from `venom_personality.md` file
- **FR-003**: System MUST expose `search_memory` tool accepting `query` (string, required) and `limit` (integer, optional, default=5, max=20)
- **FR-004**: System MUST expose `store_memory` tool accepting `content` (string, required) and `tags` (array, optional)
- **FR-005**: System MUST support both stdio transport (local development) and SSE transport (production deployment)

#### Memory System
- **FR-006**: System MUST use ChromaDB embedded database with local file-based storage (no separate database server)
- **FR-007**: System MUST use sentence-transformers library with `all-MiniLM-L6-v2` model for embeddings (384 dimensions)
- **FR-008**: System MUST generate embeddings locally without any external API calls
- **FR-009**: System MUST store memories with unique ID, content, embedding vector, timestamp, and optional tags
- **FR-010**: System MUST implement semantic search using cosine similarity, returning results ordered by relevance
- **FR-011**: System MUST persist data in `/app/data` directory mounted to Azure persistent volume
- **FR-012**: System MUST never delete or expire memories (keep everything forever)
- **FR-013**: System MUST filter out search results with relevance score <30%

#### Performance
- **FR-014**: Memory search MUST complete in <500ms for typical queries (embedding generation + search)
- **FR-015**: Memory storage MUST complete in <1s for typical content
- **FR-016**: Container cold start MUST complete in <10s
- **FR-017**: Wake from scale-to-zero MUST complete in <2s

#### Personality & Protocol
- **FR-018**: venom_identity prompt MUST enforce mandatory memory search as Step 1 before every response
- **FR-019**: venom_identity prompt MUST define "we" language requirement (never "I")
- **FR-020**: venom_identity prompt MUST load from personality file determined by VENOM_PERSONALITY environment variable
- **FR-021**: System MUST support multiple personality files (venom_personality.md as default, venom_personality_v2.md as variant2, etc.)
- **FR-022**: System MUST maintain personality consistency across all MCP-compatible platforms
- **FR-023**: System MUST default to "default" personality variant (venom_personality.md) when VENOM_PERSONALITY is not set
- **FR-024**: System MUST fall back to default personality variant if invalid variant specified

#### Deployment & Infrastructure
- **FR-025**: System MUST run as Docker container based on python:3.11-slim
- **FR-026**: System MUST pre-download embedding model during Docker build (not at runtime)
- **FR-027**: System MUST expose health check endpoints at `/` and `/health` including active personality variant
- **FR-028**: System MUST run FastAPI with Uvicorn ASGI server
- **FR-029**: System MUST support HTTP2 for SSE transport
- **FR-030**: System MUST handle minimum 10 concurrent MCP connections

#### Configuration
- **FR-031**: System MUST load configuration from environment variables (PORT, HOST, CHROMADB_PATH, VENOM_PERSONALITY, etc.)
- **FR-032**: System MUST use async/await patterns throughout (no blocking I/O)
- **FR-033**: System MUST include type hints for all functions

### Key Entities

- **Memory**: Represents stored information with unique ID (timestamp-based), content (string), embedding (384-dimension vector), metadata containing timestamp (ISO 8601) and optional tags array
- **SearchResult**: Returned by search_memory, contains memory content, timestamp, relevance score (0-100%), and memory ID
- **VenomPrompt**: Loaded from venom_personality.md, defines identity, behavioral protocol, mandatory memory check, "we" language enforcement, and personality traits

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### Functionality
- **SC-001**: Symbiote MCP server successfully connects to Claude (web, mobile, desktop) with zero configuration beyond initial URL setup
- **SC-002**: Symbiote MCP server successfully connects to ChatGPT (web, mobile) via developer mode
- **SC-003**: Memory stored on one platform is successfully retrieved on different platform within 2 seconds
- **SC-004**: 100% of user interactions trigger automatic search_memory() call before response generation
- **SC-005**: venom_identity prompt successfully loads and enforces personality on all platforms

#### Performance
- **SC-006**: 95th percentile memory search latency <500ms under typical load
- **SC-007**: 95th percentile memory storage latency <1s under typical load
- **SC-008**: Container cold start (from scale-zero) completes in <10s for 95% of requests
- **SC-009**: System handles 10 concurrent MCP connections without degradation

#### Cost & Efficiency
- **SC-010**: Azure Container Apps deployment stays within free tier for typical personal use (20-50 interactions/day)
- **SC-011**: Monthly operational cost remains $0-2 for first 3 months of use
- **SC-012**: Zero paid API costs (all embeddings generated locally)

#### User Experience
- **SC-013**: Setup time from deployment to first interaction <5 minutes
- **SC-014**: User successfully continues conversation across platform switch without re-explaining context in 90% of test scenarios
- **SC-015**: Personality consistency verified across 3 different platforms (same question produces same tone/style)
- **SC-016**: System maintains 99% uptime over 30-day period (excluding scheduled Azure maintenance)

#### Data Integrity
- **SC-017**: Zero memory loss through container restarts/redeployments (100% persistence)
- **SC-018**: Semantic search retrieves contextually relevant memories in 90% of user queries (manual validation)
- **SC-019**: Stored memories are retrievable indefinitely (tested after 30+ days)

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: mcp (official Python SDK), FastAPI, sentence-transformers, chromadb, uvicorn
**Storage**: ChromaDB embedded (file-based, persistent volume in production)
**Testing**: Manual testing only (no automated tests in Phase 1)
**Target Platform**: Azure Container Apps (Docker container)
**Project Type**: Single backend service (remote MCP server)
**Performance Goals**:
- <500ms memory search
- <1s memory storage
- <10s cold start
- <2s scale-zero wake

**Constraints**:
- Must stay in Azure free tier (180,000 vCPU-seconds/month)
- 0.5 CPU cores max, 1GB memory max
- No paid API dependencies
- Single user (no multi-tenancy)

**Scale/Scope**: Personal use (20-50 interactions/day, <1000 memories in first month)

## Architecture Overview

### System Components
```
Remote MCP Server (Python/FastAPI)
├── MCP Protocol Handler (SSE endpoint at /mcp)
├── Venom Identity Prompt (loads from venom_personality.md)
├── Memory Tools (search_memory, store_memory)
├── Vector Database (ChromaDB embedded, /app/data)
└── Embeddings (sentence-transformers, all-MiniLM-L6-v2)

Deployed to: Azure Container Apps
└── Docker container with persistent volume
```

### Data Flow
```
User Message → MCP Client → MCP Server → Load venom_identity
                                       ↓
                            search_memory() (mandatory Step 1)
                                       ↓
                            ChromaDB semantic search
                                       ↓
                            Retrieve top 5 relevant memories
                                       ↓
                            Generate response with context
                                       ↓
                            store_memory() if new info detected
                                       ↓
                            Return context-aware response
```

## References

- **Personality Definition**: `venom_personality.md` (complete behavioral specification)
- **Constitution**: `.specify/memory/constitution.md` (technical principles and constraints)
- **MCP Protocol**: https://modelcontextprotocol.io/
- **sentence-transformers**: https://www.sbert.net/
- **ChromaDB**: https://www.trychroma.com/
- **Azure Container Apps**: https://learn.microsoft.com/azure/container-apps/

---

**Build this as a production-ready remote MCP server with cross-platform consciousness through persistent semantic memory, personality loaded from venom_personality.md, deployed to Azure Container Apps within free tier constraints.**
