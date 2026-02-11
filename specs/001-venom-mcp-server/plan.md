# Implementation Plan: Symbiote MCP Server

**Branch**: `001-symbiote-mcp-server` | **Date**: 2026-01-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-symbiote-mcp-server/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a production-ready remote MCP server that provides cross-platform AI consciousness through persistent semantic memory. The server exposes the MCP protocol via SSE, serves the Venom personality from venom_personality.md, and implements search_memory/store_memory tools backed by ChromaDB vector database with sentence-transformers embeddings. Deployed to Azure Container Apps with scale-to-zero within free tier constraints.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: mcp (official Python SDK), FastAPI, sentence-transformers, chromadb, uvicorn
**Storage**: ChromaDB embedded (file-based, persistent volume in production at /app/data)
**Testing**: Manual testing only (no automated tests in Phase 1)
**Target Platform**: Azure Container Apps (Docker container, Linux)
**Project Type**: Single backend service (remote MCP server)
**Performance Goals**:
- Memory search: <500ms
- Memory storage: <1s
- Container cold start: <10s
- Scale-zero wake: <2s
- Embedding generation: <1s per text

**Constraints**:
- Must stay in Azure free tier (180,000 vCPU-seconds/month)
- 0.5 CPU cores max, 1GB memory max
- No paid API dependencies
- Single user (no multi-tenancy)

**Scale/Scope**: Personal use (20-50 interactions/day, <1000 memories in first month)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Python-First Development
- ✅ **PASS**: Python 3.11+ only, no other languages
- ✅ **PASS**: Async/await patterns throughout (FastAPI, Uvicorn)
- ✅ **PASS**: Type hints required for all functions
- ✅ **PASS**: Pure Python stack leveraging AI/ML ecosystem

### Principle II: Remote MCP Architecture
- ✅ **PASS**: Remote MCP server via HTTP/SSE (not local stdio)
- ✅ **PASS**: Single responsibility per module (server, memory, prompts)
- ✅ **PASS**: Stateless server design (state in ChromaDB only)

### Principle III: Vector Memory System
- ✅ **PASS**: Vector-based semantic search using sentence-transformers
- ✅ **PASS**: Free local embeddings (no paid APIs)
- ✅ **PASS**: Persistent storage via Azure persistent volume
- ✅ **PASS**: No memory expiration or cleanup

### Principle IV: Zero-Cost Deployment
- ✅ **PASS**: Azure Container Apps with scale-to-zero
- ✅ **PASS**: Docker containerization
- ✅ **PASS**: Single container instance (no orchestration)
- ✅ **PASS**: Staying within free tier constraints

### Principle V: Symbiotic Personality
- ✅ **PASS**: Personality defined in venom_personality.md
- ✅ **PASS**: Server reads and serves via MCP prompts automatically
- ✅ **PASS**: "We" language enforced in personality file
- ✅ **PASS**: Mandatory memory check protocol defined

### Principle VI: Simplicity & Educational Value
- ✅ **PASS**: Simple over clever (embedded ChromaDB vs separate server)
- ✅ **PASS**: Educational value (learning MCP, vectors, Azure)
- ✅ **PASS**: Clear module separation and naming

### Non-Negotiable Rules Compliance
1. ✅ "We" language - enforced via venom_personality.md
2. ✅ Memory check before response - defined in personality protocol
3. ✅ No paid APIs - sentence-transformers is free and local
4. ✅ No data loss - persistent volume mounted
5. ✅ Auto-served personality - MCP prompts mechanism
6. ✅ Free tier compliance - resource limits configured
7. ✅ Same personality everywhere - single prompt source
8. ✅ Semantic search - cosine similarity via ChromaDB
9. ✅ Personality from file - venom_personality.md as source
10. ✅ Async/await - FastAPI and async Python throughout

**GATE STATUS: ✅ PASS - All constitutional requirements satisfied**

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
symbiote-mcp/
├── Dockerfile                    # Container definition
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .gitignore                    # Git exclusions
├── README.md                     # Setup instructions
├── venom_personality.md          # Default personality (variant: "default")
├── venom_personality_v2.md       # Alternative personality (variant: "variant2")
│
├── src/
│   ├── __init__.py
│   ├── server.py                 # Main FastAPI + MCP server entry point
│   ├── config.py                 # Configuration management (env vars)
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── store.py              # ChromaDB CRUD operations
│   │   └── embeddings.py         # sentence-transformers wrapper
│   │
│   └── prompts/
│       ├── __init__.py
│       └── venom.py              # Load personality from venom_personality.md
│
├── tests/
│   └── manual_testing.md         # Manual test scenarios
│
└── docs/
    └── learning/                 # Educational documentation per ai_agent_learning_protocol.md
        ├── 00-overview.md
        ├── 01-mcp-server-design.md
        ├── 01-mcp-server-implementation.md
        ├── 01-mcp-server-decisions.md
        ├── 02-embeddings-design.md
        ├── 02-embeddings-implementation.md
        ├── 02-embeddings-decisions.md
        ├── 03-chromadb-design.md
        ├── 03-chromadb-implementation.md
        ├── 03-chromadb-decisions.md
        ├── 04-mcp-prompts-design.md
        ├── 04-mcp-prompts-implementation.md
        ├── 04-mcp-prompts-decisions.md
        ├── 05-docker-design.md
        ├── 05-docker-implementation.md
        ├── 05-docker-decisions.md
        └── 99-glossary.md
```

**Structure Decision**: Single project structure (Option 1) selected. This is a backend-only Python service with no frontend. The structure follows the constitution's required layout with clear separation: `src/server.py` for entry point, `src/config.py` for all configuration, `src/memory/` for memory operations (embeddings + storage), and `src/prompts/` for personality loading. The `docs/learning/` directory supports the ai_agent_learning_protocol.md requirement for educational documentation generation.

### Personality Experimentation Support

**Feature**: Environment variable-based personality variant switching

**Implementation**:
- `VENOM_PERSONALITY` environment variable selects which personality file to load
- Default value: `"default"` (loads `venom_personality.md`)
- Alternative variants: `"variant2"` (loads `venom_personality_v2.md`)
- Invalid variants fall back to default with warning log

**Usage**:
```bash
# Use default personality
python src/server.py
# or explicitly
VENOM_PERSONALITY=default python src/server.py

# Use alternative personality
VENOM_PERSONALITY=variant2 python src/server.py
```

**Health Check Integration**:
```json
GET /health
{
  "status": "healthy",
  "server_name": "symbiote-mcp",
  "personality_variant": "variant2",
  ...
}
```

**Constitutional Compliance**:
- ✅ Simple (one env var, no code complexity)
- ✅ Single source of truth (each variant is one file)
- ✅ No API changes (still exposes single `venom_identity` prompt)
- ✅ Easy to test and compare variants
- ✅ Requires server restart to switch (stateless design maintained)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No complexity violations** - All constitutional requirements are satisfied. The design uses simple, proven technologies (FastAPI, ChromaDB embedded, sentence-transformers) with minimal abstraction layers. No unnecessary patterns or additional complexity introduced.

---

## Phase 0: Research (Completed)

**Status**: ✅ Complete

**Output**: [research.md](./research.md)

**Summary**:
- All technology choices documented with rationale
- No unknowns or NEEDS CLARIFICATION items (all technologies well-established)
- Alternatives evaluated for each decision
- Best practices identified for MCP, embeddings, vector DB, FastAPI, and Azure deployment
- Performance considerations and cost analysis completed

---

## Phase 1: Design & Contracts (Completed)

**Status**: ✅ Complete

**Outputs**:
- [data-model.md](./data-model.md) - Complete entity definitions with validation rules
- [contracts/mcp-schema.json](./contracts/mcp-schema.json) - MCP tools and prompts API contracts
- [quickstart.md](./quickstart.md) - Step-by-step setup and deployment guide
- [CLAUDE.md](../../CLAUDE.md) - Agent context file updated with tech stack

**Data Model**:
- 4 core entities: Memory, MemoryMetadata, SearchResult, VenomPrompt
- Simple 1:1 relationships, no complex joins
- ChromaDB single collection design
- Clear validation rules and constraints

**API Contracts**:
- 1 prompt: `venom_identity` (loads from venom_personality.md)
- 2 tools: `search_memory` and `store_memory`
- 3 HTTP endpoints: `/mcp` (SSE), `/health`, `/`
- Complete JSON schemas with examples and error cases

**Quickstart**:
- Local setup in <10 minutes
- Azure deployment guide with all commands
- Verification checklist and troubleshooting

---

## Post-Design Constitution Check

**Status**: ✅ PASS (Re-evaluated after Phase 1 design)

All constitutional principles remain satisfied:
- ✅ Python-first development with async/await and type hints
- ✅ Remote MCP architecture with stateless design
- ✅ Vector memory system with free local embeddings
- ✅ Zero-cost deployment on Azure Container Apps
- ✅ Symbiotic personality from venom_personality.md
- ✅ Simplicity & educational value maintained

**No changes to constitutional compliance** - Design adheres to all principles.

---

## Next Steps

**Phase 2: Task Generation** (Not part of this command)
- Run `/speckit.tasks` to generate dependency-ordered tasks.md
- Tasks will reference these design artifacts for implementation

**Phase 3: Implementation** (After tasks.md)
- Run `/speckit.implement` to execute tasks
- Follow ai_agent_learning_protocol.md for educational documentation
- Generate design/implementation/decision docs for each component
