<!--
Sync Impact Report:
- Version change: Initial → 1.0.0
- This is the initial constitution for Venom MCP Server
- Modified principles: N/A (initial creation)
- Added sections: All core sections established
- Templates requiring updates:
  ✅ constitution.md created
  ⚠ plan-template.md - will need constitution check gates defined
  ⚠ spec-template.md - aligned with technical constraints
  ⚠ tasks-template.md - aligned with development workflow
- Follow-up TODOs: None - all placeholders filled based on venom_constitution.md
-->

# Venom MCP Server Constitution

## Core Principles

### I. Python-First Development
**Python 3.11+** as the primary and only language. All code MUST use async/await patterns throughout. Type hints are REQUIRED for all functions. No JavaScript/TypeScript - pure Python stack only. This ensures consistency, simplifies the stack, and leverages Python's superior AI/ML ecosystem for vector embeddings.

**Rationale**: Vector embeddings are native to Python, ChromaDB is Python-first, and avoiding language bridges reduces complexity. This also serves the educational goal of learning Python for AI/ML applications.

### II. Remote MCP Architecture
The server MUST be a **Remote MCP Server** accessible via HTTP/SSE, not local stdio. Architecture MUST follow single responsibility per module with clear separation of concerns: server, memory, and prompts. Server design MUST be stateless with all state persisted in ChromaDB only.

**Rationale**: Remote architecture enables mobile access (critical requirement), allows one deployment to serve all platforms, and enables true cross-platform consciousness without per-device setup.

### III. Vector Memory System
Memory MUST use **vector-based semantic search** not keyword search. Embeddings MUST be free and local using sentence-transformers. No paid APIs for embeddings are permitted. Storage MUST be persistent and survive restarts. Memory MUST never expire or be cleaned up - keep everything forever.

**Rationale**: Semantic search provides better context retrieval than keywords. Free local embeddings avoid API costs and rate limits. Persistent storage ensures continuity of the symbiote's memory across sessions.

### IV. Zero-Cost Deployment
Deployment MUST use **Azure Container Apps** (not Functions, not VMs) with scale-to-zero capability. All solutions MUST use Docker containerization with single container instances (no orchestration). The entire system MUST stay within Azure free tier limits.

**Rationale**: Azure Container Apps provides better cold start performance than Functions, is more managed than VMs, scales to zero for cost savings, and is industry-relevant learning.

### V. Symbiotic Personality
Personality MUST be defined in a separate `venom_personality.md` file. Server MUST read and serve personality automatically via MCP prompts mechanism. **"We" language is MANDATORY** (enforcing symbiote metaphor). Memory check is REQUIRED before every response.

**Rationale**: MCP prompts inject personality automatically, ensuring consistency across all platforms without manual setup. The symbiote metaphor creates the intended user experience of "one consciousness."

### VI. Simplicity & Educational Value
Code MUST prioritize simple over clever, readable over performant (unless performance truly matters). Comments MUST explain "why" not "what". No premature optimization. Every technology choice MUST have educational value.

**Rationale**: Simple code is maintainable code. Educational value ensures learning from every component choice. Complexity must be justified or rejected.

## Technical Constraints

### Database Requirements
- **ChromaDB embedded** (no separate database server)
- Local file-based storage only
- Single collection: `venom_memories`
- No external database dependencies
- Persistent volume REQUIRED in production

### Embeddings Requirements
- **sentence-transformers library** only
- Model: `all-MiniLM-L6-v2` (384 dimensions)
- Free, local, no API calls
- Pre-download during Docker build
- No model switching or customization

### MCP Protocol Requirements
- Use official `mcp` Python package
- Support both stdio (dev) and SSE (prod) transports
- Expose prompts: `venom_identity`
- Expose tools: `search_memory`, `store_memory`
- Follow MCP specification strictly

### Web Framework Requirements
- **FastAPI** for HTTP endpoints only
- Uvicorn as ASGI server
- SSE support for MCP protocol
- Health check endpoints REQUIRED
- No GraphQL, no REST API beyond MCP

### Security Model
- Public endpoint (no auth for personal use)
- Trust Azure security for data
- No memory encryption
- Single user assumption
- No multi-tenancy

## Performance Standards

### Response Time Targets
- Memory search: < 500ms
- Memory storage: < 1s
- Container cold start: < 10s
- Wake from scale-zero: < 2s
- Embedding generation: < 1s per text

### Resource Limits
- CPU: 0.5 cores maximum
- Memory: 1 GB maximum
- Storage: 2 GB persistent volume
- Concurrent connections: 10 minimum

### Cost Constraints
- MUST stay in Azure free tier
- No paid API dependencies
- Target: $0-2/month operational cost
- 180,000 vCPU-seconds/month limit

## Project Structure

### Required Directory Layout
```
venom-mcp/
├── Dockerfile
├── requirements.txt
├── .env.example
├── venom_personality.md    # Personality definition (reference)
├── src/
│   ├── server.py           # Main entry point
│   ├── config.py           # All configuration
│   ├── memory/             # Memory operations
│   └── prompts/            # Prompt loading
└── tests/                  # Manual testing only
```

### Module Responsibilities
- `server.py`: FastAPI app + MCP handlers ONLY
- `config.py`: ALL environment variables and settings
- `memory/store.py`: ChromaDB CRUD operations
- `memory/embeddings.py`: sentence-transformers wrapper
- `prompts/venom.py`: Load venom_personality.md file

### File Naming Conventions
- Snake_case for Python files
- Lowercase for directories
- No abbreviations unless standard (e.g., `mcp`, `api`)
- Descriptive names over short names

## Development Workflow

### Local Development Process
1. Python virtual environment (venv)
2. requirements.txt for dependencies
3. .env for local configuration
4. stdio transport for Claude Desktop testing
5. Manual testing (no automated tests yet)

### Production Deployment Process
1. Docker build with multi-stage if needed
2. Azure Container Apps deployment
3. Persistent volume mounted
4. Environment variables via Azure
5. SSE transport for remote clients

### Version Control Standards
- Git for source control
- .gitignore for Python, ChromaDB, env files
- No secrets in repository
- README.md with setup instructions
- venom_personality.md tracked in repo

## Scope Boundaries

### Explicitly Out of Scope
The following features are FORBIDDEN in current implementation:
- ❌ Multi-user support
- ❌ Authentication/authorization
- ❌ Memory encryption
- ❌ Memory cleanup/pruning
- ❌ Custom embedding models
- ❌ Web dashboard UI
- ❌ Analytics/monitoring beyond health checks
- ❌ Automated tests (manual only)
- ❌ Memory import/export
- ❌ Multiple collections
- ❌ Memory versioning
- ❌ Advanced search filters
- ❌ Rate limiting
- ❌ Usage quotas

### Future Phases Only
These MAY be considered after core functionality is proven:
- Multi-user support
- Enhanced security
- Memory management tools
- Analytics dashboard
- Automated testing
- CI/CD pipeline

## Success Criteria

### Must Have (Non-Negotiable)
- ✅ Works on Claude web, mobile, desktop
- ✅ Works on ChatGPT web, mobile
- ✅ Same memories across all platforms
- ✅ Same personality across all platforms
- ✅ Memory search < 500ms
- ✅ Stays in Azure free tier
- ✅ Zero setup after initial deployment
- ✅ Personality auto-loaded via MCP prompts

### Nice to Have
- Graceful error messages
- Helpful logging for debugging
- Clear documentation
- Example interactions in README

### Success Metrics
- Setup time < 5 minutes (after deployment)
- User says "feels like one AI" not "good memory"
- No re-explaining context across platforms
- Daily use for 3+ months without issues

## Design Philosophy

### Simplicity First
- Choose simple solutions over complex ones
- Avoid abstractions until needed
- One file per clear responsibility
- Direct code over frameworks when possible

### Educational Value
- Every technology choice teaches something
- Learn MCP protocol hands-on
- Learn vector databases practically
- Learn Azure deployment real-world

### User Experience
- Invisible technology
- "Just works" feeling
- No configuration burden
- Consistent across platforms
- Fast enough to feel instant

### Maintainability
- Code should be self-documenting
- Comments explain decisions
- Easy to modify later
- Clear separation of concerns
- No hidden magic

## Non-Negotiable Rules

The following rules MUST NEVER be violated:

1. **Always use "we" language** in Venom responses
2. **Always check memory before responding** (mandatory protocol)
3. **Never use paid APIs** for embeddings
4. **Never lose data** on container restart
5. **Never require manual personality entry** (auto-served via MCP)
6. **Always stay in free tier** costs
7. **Always maintain same personality** across platforms
8. **Always use semantic search** (not keyword matching)
9. **Always read personality from venom_personality.md** (single source of truth)
10. **Always async/await** for I/O operations

## Values Hierarchy

When principles conflict, prioritize in this order:

1. **User Experience** - Invisible, fast, consistent
2. **Simplicity** - Simple beats clever
3. **Learning** - Educational value matters
4. **Cost** - Stay free/cheap
5. **Performance** - Good enough beats perfect
6. **Features** - Core use case only

## Governance

### Amendment Process
This constitution guides ALL technical decisions. Amendments REQUIRE:
- Documentation of proposed change with rationale
- Review of impact on dependent templates and code
- Version bump following semantic versioning
- Migration plan if existing code affected

### Compliance Verification
- All PRs and code reviews MUST verify compliance with constitution
- Any complexity introduced MUST be justified against principles
- Use [.specify/memory/constitution.md] as the authoritative source
- When in doubt, prioritize the Values Hierarchy

### Version Policy
- MAJOR: Backward incompatible governance/principle changes
- MINOR: New principles added or existing ones materially expanded
- PATCH: Clarifications, wording improvements, typo fixes

**Version**: 1.0.0 | **Ratified**: 2026-01-25 | **Last Amended**: 2026-01-25
