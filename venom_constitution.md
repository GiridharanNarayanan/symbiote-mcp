# Venom MCP Server - Project Constitution

## Core Principles

### Language & Runtime
- **Python 3.11+** as the primary language
- Async/await patterns throughout
- Type hints required for all functions
- No JavaScript/TypeScript - pure Python stack

### Architecture Philosophy
- **Remote MCP Server** (not local stdio)
- Single responsibility per module
- Separation of concerns: server, memory, prompts
- Stateless server design (state in ChromaDB only)

### Memory System
- **Vector-based semantic search** (not keyword search)
- Free, local embeddings (sentence-transformers)
- No paid APIs for embeddings
- Persistent storage required (survives restarts)
- No memory expiration or cleanup (keep everything)

### Deployment Strategy
- **Azure Container Apps** (not Functions, not VMs)
- Scale-to-zero capability
- Docker containerization
- Single container instance (no orchestration)
- Stay within free tier limits

### Personality & Behavior
- Personality defined in separate `venom_personality.md` file
- Server reads and serves personality automatically
- MCP prompts mechanism for identity injection
- **"We" language enforced** (symbiote metaphor)
- Mandatory memory check before every response

### Code Quality Standards
- Simple over clever
- Readable over performant (unless performance matters)
- Comments explain "why" not "what"
- No premature optimization
- Educational value in every component choice

## Technical Constraints

### Database
- **ChromaDB embedded** (no separate database server)
- Local file-based storage
- Single collection: `venom_memories`
- No external database dependencies
- Persistent volume in production

### Embeddings
- **sentence-transformers library**
- Model: `all-MiniLM-L6-v2` (384 dimensions)
- Free, local, no API calls
- Pre-download during Docker build
- No model switching or customization

### MCP Protocol
- Use official `mcp` Python package
- Support both stdio (dev) and SSE (prod) transports
- Expose prompts: `venom_identity`
- Expose tools: `search_memory`, `store_memory`
- Follow MCP specification strictly

### Web Framework
- **FastAPI** for HTTP endpoints
- Uvicorn as ASGI server
- SSE support for MCP protocol
- Health check endpoints required
- No GraphQL, no REST API beyond MCP

### Security Model
- Public endpoint (no auth for personal use)
- Trust Azure security for data
- No memory encryption
- Single user assumption
- No multi-tenancy

## Performance Targets

### Response Times
- Memory search: < 500ms
- Memory storage: < 1s
- Container cold start: < 10s
- Wake from scale-zero: < 2s
- Embedding generation: < 1s per text

### Resource Limits
- CPU: 0.5 cores max
- Memory: 1 GB max
- Storage: 2 GB persistent volume
- Concurrent connections: 10 minimum

### Cost Constraints
- Must stay in Azure free tier
- No paid API dependencies
- Target: $0-2/month operational cost
- 180,000 vCPU-seconds/month limit

## Project Structure Rules

### Directory Layout
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
- `server.py`: FastAPI app + MCP handlers only
- `config.py`: All environment variables and settings
- `memory/store.py`: ChromaDB CRUD operations
- `memory/embeddings.py`: sentence-transformers wrapper
- `prompts/venom.py`: Load venom_personality.md file

### File Naming
- Snake_case for Python files
- Lowercase for directories
- No abbreviations unless standard (e.g., `mcp`, `api`)
- Descriptive names over short names

## Development Workflow

### Local Development
1. Python virtual environment (venv)
2. requirements.txt for dependencies
3. .env for local configuration
4. stdio transport for Claude Desktop testing
5. Manual testing (no automated tests yet)

### Production Deployment
1. Docker build with multi-stage if needed
2. Azure Container Apps deployment
3. Persistent volume mounted
4. Environment variables via Azure
5. SSE transport for remote clients

### Version Control
- Git for source control
- .gitignore for Python, ChromaDB, env files
- No secrets in repository
- README.md with setup instructions
- venom_personality.md tracked in repo

## What We DON'T Build

### Explicitly Out of Scope
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
- Multi-user support
- Enhanced security
- Memory management tools
- Analytics dashboard
- Automated testing
- CI/CD pipeline

## Success Criteria

### Must Have
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

## Technology Decisions

### Why Python?
- Vector embeddings native to Python
- ChromaDB is Python-first
- No language bridge complexity
- Better AI/ML ecosystem
- Personal learning goal

### Why ChromaDB Embedded?
- No separate server to manage
- Simple file-based storage
- Good enough for personal use
- Easy local development
- Portable data

### Why sentence-transformers?
- Free and local
- No API costs
- No rate limits
- Fast enough for personal use
- Industry standard

### Why Azure Container Apps?
- Better than Functions (no cold starts)
- Better than VMs (managed platform)
- Scale-to-zero saves money
- Free tier sufficient
- Industry-relevant skill

### Why Remote MCP?
- Works on mobile (critical requirement)
- One deployment, all platforms
- True cross-platform consciousness
- No per-device setup

## Non-Negotiable Rules

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

When in conflict, prioritize in this order:

1. **User Experience** - Invisible, fast, consistent
2. **Simplicity** - Simple beats clever
3. **Learning** - Educational value matters
4. **Cost** - Stay free/cheap
5. **Performance** - Good enough beats perfect
6. **Features** - Core use case only

---

**This constitution guides all technical decisions for the Venom MCP Server project. Every code choice, architecture decision, and feature prioritization should align with these principles.**
