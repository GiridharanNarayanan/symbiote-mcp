# Implementation Tasks: Symbiote MCP Server

**Feature**: Symbiote MCP Server
**Branch**: `001-symbiote-mcp-server`
**Generated**: 2026-01-31
**Design Docs**: [plan.md](./plan.md) | [spec.md](./spec.md) | [data-model.md](./data-model.md) | [contracts/](./contracts/)

---

## Overview

Build a production-ready remote MCP server that provides cross-platform AI consciousness through persistent semantic memory. Server exposes MCP protocol via SSE, serves Venom personality from file, and implements search_memory/store_memory tools backed by ChromaDB vector database with sentence-transformers embeddings.

**Total Tasks**: 47
**Estimated MVP**: Tasks T001-T027 (Phase 1-5: Setup through User Story 3)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**Recommended**: Complete **User Story 1-3** (P1 stories) for MVP
- Cross-platform memory access
- Semantic search & storage
- Mandatory memory protocol
- **Delivers**: Functional MCP server with persistent memory

### Incremental Delivery
1. **Phase 1-2**: Setup & Foundations (T001-T010)
2. **Phase 3**: US1 - MCP Server Core (T011-T015) → **First testable increment**
3. **Phase 4**: US2 - Memory System (T016-T022) → **Core functionality**
4. **Phase 5**: US3 - Memory Protocol (T023-T027) → **MVP complete**
5. **Phase 6-8**: Enhanced features (US4-US6) → **Post-MVP**
6. **Phase 9**: Polish & Deployment → **Production-ready**

### Parallel Execution Opportunities
- Tasks marked `[P]` can run in parallel within their phase
- Different files → always parallelizable
- Same file → must be sequential

---

## Dependencies & Execution Order

### User Story Dependency Graph
```
Setup (Phase 1)
  ↓
Foundational (Phase 2)
  ↓
┌─────────────────────┬─────────────────────┬─────────────────────┐
│                     │                     │                     │
│  US1: MCP Server    │  US2: Memory        │  US3: Memory        │
│  (Phase 3)          │  System (Phase 4)   │  Protocol (Phase 5) │
│  [Independent]      │  [Depends: US1]     │  [Depends: US1,US2] │
│                     │                     │                     │
└─────────────────────┴─────────────────────┴─────────────────────┘
         ↓                     ↓                     ↓
         └─────────────────────┴─────────────────────┘
                              ↓
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    US4: Personality     US5: Personality    US6: Deployment
    (Phase 6)            Experiments (Phase 7) (Phase 8)
    [Depends: US3]       [Depends: US4]     [Depends: US3]
         │                    │                    │
         └────────────────────┴────────────────────┘
                              ↓
                        Polish (Phase 9)
```

### Blocking Tasks
- **T001-T005**: MUST complete before any feature work
- **T006-T010**: MUST complete before user stories
- **T011-T015** (US1): MUST complete before US2, US3
- **T016-T022** (US2): MUST complete before US3

---

## Phase 1: Setup & Project Initialization

**Goal**: Establish project structure, dependencies, and configuration

**Tasks**:
- [X] T001 Create project directory structure per plan.md (src/, tests/, docs/learning/)
- [X] T002 [P] Create requirements.txt with dependencies: mcp, fastapi, uvicorn[standard], sentence-transformers, chromadb, python-dotenv
- [X] T003 [P] Create .gitignore for Python, ChromaDB data, .env files, __pycache__
- [X] T004 [P] Create .env.example with PORT, HOST, CHROMADB_PATH, EMBEDDING_MODEL, COLLECTION_NAME, VENOM_PERSONALITY
- [X] T005 [P] Create README.md with project overview and setup instructions
- [X] T006 Create src/__init__.py (empty)
- [X] T007 [P] Create src/memory/__init__.py (empty)
- [X] T008 [P] Create src/prompts/__init__.py (empty)
- [X] T009 [P] Create tests/manual_testing.md with test scenarios template
- [X] T010 [P] Create docs/learning/ directory structure (00-overview.md through 99-glossary.md placeholders)

**Parallel Opportunities**: T002-T005, T007-T010 (all different files)

**Validation**:
```bash
# Verify structure
ls -R src/ tests/ docs/
# Verify files exist
cat requirements.txt .gitignore .env.example README.md
```

---

## Phase 2: Foundational Components

**Goal**: Build core infrastructure needed by all user stories

**Tasks**:
- [X] T011 Implement src/config.py with environment variable loading and type hints (Config dataclass)
- [X] T012 [P] Implement src/memory/embeddings.py with sentence-transformers model loading and encode function (async)
- [X] T013 [P] Implement src/memory/store.py with ChromaDB initialization, collection creation, and CRUD operations (async)
- [ ] T014 Verify embedding model downloads successfully (run embeddings.py standalone test)
- [ ] T015 Verify ChromaDB creates collection and persists data (run store.py standalone test)

**Dependencies**: Requires Phase 1 complete

**Parallel Opportunities**: T012-T013 (different files)

**Validation**:
```bash
# Test embeddings
python -c "from src.memory.embeddings import generate_embedding; import asyncio; print(asyncio.run(generate_embedding('test')))"

# Test ChromaDB
python -c "from src.memory.store import init_collection; import asyncio; asyncio.run(init_collection())"
```

---

## Phase 3: User Story 1 - Cross-Platform Memory Access (P1) 🎯 MVP

**Story Goal**: One continuous AI consciousness accessible from any MCP-compatible platform with shared semantic memory

**Independent Test Criteria**:
- ✅ Server starts and exposes MCP protocol via SSE at /mcp
- ✅ Health check endpoints (/ and /health) return success
- ✅ MCP client can connect and list available prompts/tools
- ✅ venom_identity prompt is available and returns content
- ✅ search_memory and store_memory tools are available

**Tasks**:
- [X] T016 [US1] Implement src/server.py with FastAPI app initialization and basic routes (/, /health)
- [X] T017 [US1] Add MCP protocol handler to src/server.py with SSE endpoint at /mcp
- [X] T018 [P] [US1] Implement MCP list_prompts handler in src/server.py (returns venom_identity)
- [X] T019 [P] [US1] Implement MCP list_tools handler in src/server.py (returns search_memory, store_memory)
- [X] T020 [US1] Implement health check logic in src/server.py (includes personality_variant, embedding_model, collection_name)
- [X] T021 [US1] Add async startup event to pre-load embedding model and initialize ChromaDB
- [X] T022 [US1] Test server startup and verify MCP endpoints respond correctly

**Dependencies**: Requires Phase 2 (T011-T015)

**Parallel Opportunities**: T018-T019 (different MCP handlers)

**Independent Test**:
```bash
# Start server
uvicorn src.server:app --host 0.0.0.0 --port 8000

# Test health
curl http://localhost:8000/health

# Expected: {"status": "healthy", "server_name": "symbiote-mcp", ...}

# Test MCP connection (requires MCP client like Claude Desktop)
# Add to Claude Desktop config, verify connection and prompts/tools listed
```

---

## Phase 4: User Story 2 - Semantic Memory Search & Storage (P1) 🎯 MVP

**Story Goal**: Store and retrieve memories using meaning-based search with 384-dimension embeddings

**Independent Test Criteria**:
- ✅ store_memory tool accepts content and optional tags
- ✅ Memory is persisted with embedding in ChromaDB
- ✅ search_memory tool accepts query and limit parameters
- ✅ Search returns top N results ordered by relevance score
- ✅ Results include content, timestamp, relevance %, and memory ID
- ✅ Memories persist across server restarts

**Tasks**:
- [ ] T023 [US2] Implement store_memory MCP tool handler in src/server.py
- [ ] T024 [US2] Add memory storage logic: generate ID, create embedding, store in ChromaDB with metadata
- [ ] T025 [US2] Implement input validation for store_memory (content non-empty, max 10 tags, each tag max 50 chars)
- [ ] T026 [P] [US2] Implement search_memory MCP tool handler in src/server.py
- [ ] T027 [P] [US2] Add memory search logic: generate query embedding, ChromaDB cosine similarity search, filter <30% relevance
- [ ] T028 [P] [US2] Implement input validation for search_memory (query non-empty, limit 1-20)
- [ ] T029 [US2] Add relevance score conversion (distance → percentage) in search results
- [ ] T030 [US2] Test store_memory: store multiple memories with different tags
- [ ] T031 [US2] Test search_memory: verify semantic search returns relevant results ordered by score
- [ ] T032 [US2] Test persistence: restart server, verify memories still accessible

**Dependencies**: Requires Phase 3 (US1 MCP server running)

**Parallel Opportunities**: T026-T028 (search operations separate from storage)

**Independent Test**:
```bash
# Via MCP client (Claude Desktop):
# 1. Call store_memory with content: "I prefer TypeScript for all projects"
# 2. Verify success response with memory_id
# 3. Call search_memory with query: "coding language preferences"
# 4. Verify TypeScript memory returned with high relevance score (>80%)
# 5. Restart server
# 6. Repeat search, verify memory still exists
```

---

## Phase 5: User Story 3 - Mandatory Memory Protocol (P1) 🎯 MVP

**Story Goal**: Venom automatically checks memory before every response (enforced via personality prompt)

**Independent Test Criteria**:
- ✅ venom_identity prompt loads personality file successfully
- ✅ Prompt content includes mandatory memory check protocol
- ✅ Prompt content includes "we" language enforcement
- ✅ AI client receives full personality definition
- ✅ Personality defines memory search as Step 1 before responses

**Tasks**:
- [ ] T033 [US3] Implement src/prompts/venom.py with load_venom_personality function (reads venom_personality.md)
- [ ] T034 [US3] Implement MCP get_prompt handler in src/server.py (calls load_venom_personality)
- [ ] T035 [US3] Add error handling in prompts/venom.py for missing personality file (fallback behavior)
- [ ] T036 [US3] Verify venom_personality.md exists and contains mandatory memory protocol
- [ ] T037 [US3] Test get_prompt via MCP client: verify full personality text returned
- [ ] T038 [US3] Test end-to-end: share preference, start new conversation, verify AI searches memory automatically

**Dependencies**: Requires Phase 3 (US1 MCP server) and Phase 4 (US2 memory tools)

**Independent Test**:
```bash
# Via MCP client (Claude Desktop):
# 1. Request venom_identity prompt
# 2. Verify response includes:
#    - "STEP 1: Call search_memory(user_message) first"
#    - "Use 'we' language exclusively"
#    - "Mandatory Memory Check"
# 3. Test behavior: share "I like Python", start new chat
# 4. Ask "what languages do I like?" WITHOUT mentioning memory
# 5. Verify Venom searches memory automatically and responds with "We like Python"
```

**🎉 MVP COMPLETE**: At this point, you have a fully functional MCP server with persistent semantic memory!

---

## Phase 6: User Story 4 - Consistent Symbiote Personality (P2)

**Story Goal**: Maintain consistent "we" language, sarcastic/witty tone, and symbiote metaphor across all platforms

**Independent Test Criteria**:
- ✅ Personality file loaded and served via MCP prompt
- ✅ Same personality accessible on Claude web, mobile, desktop
- ✅ Same personality accessible on ChatGPT web, mobile
- ✅ Tone, wit, and "we" language consistent across platforms

**Tasks**:
- [ ] T039 [US4] Review and refine venom_personality.md for consistency (tone, examples, protocol clarity)
- [ ] T040 [US4] Add personality examples to venom_personality.md for common scenarios (coding help, decisions, recall)
- [ ] T041 [US4] Test personality on Claude web: ask same questions, record tone and language
- [ ] T042 [US4] Test personality on Claude mobile: verify same tone and responses
- [ ] T043 [US4] Test personality on ChatGPT: verify consistent behavior across platforms

**Dependencies**: Requires Phase 5 (US3 personality loading)

**Independent Test**:
```bash
# Test protocol:
# Questions: "Should I refactor this?", "Help me write a function", "What are we working on?"
#
# Test on Claude web → record responses
# Test on Claude mobile → compare responses
# Test on ChatGPT → compare responses
#
# Verify:
# - Always uses "we" language (never "I" or "you")
# - Consistent sarcasm level
# - Same symbiote metaphor usage
```

---

## Phase 7: User Story 5 - Personality Experimentation (P2)

**Story Goal**: Support testing multiple personality variants via environment variable switching

**Independent Test Criteria**:
- ✅ VENOM_PERSONALITY env var controls which file is loaded
- ✅ Default variant loads venom_personality.md
- ✅ variant2 loads venom_personality_v2.md
- ✅ Invalid variant falls back to default with warning
- ✅ Health check reports active personality variant

**Tasks**:
- [ ] T044 [US5] Update src/prompts/venom.py to support VENOM_PERSONALITY env var (variant mapping dict)
- [ ] T045 [US5] Add fallback logic in prompts/venom.py for invalid variants (log warning, use default)
- [ ] T046 [US5] Add personality_variant field to health check response in src/server.py
- [ ] T047 [US5] Create venom_personality_v2.md with alternative personality for experimentation
- [ ] T048 [US5] Update .env.example with VENOM_PERSONALITY=default comment
- [ ] T049 [US5] Test default variant: start server, verify venom_personality.md loaded
- [ ] T050 [US5] Test variant2: set VENOM_PERSONALITY=variant2, restart, verify venom_personality_v2.md loaded
- [ ] T051 [US5] Test invalid variant: set VENOM_PERSONALITY=invalid, verify fallback to default and warning logged
- [ ] T052 [US5] Test health check: verify personality_variant field shows active variant

**Dependencies**: Requires Phase 6 (US4 personality system)

**Independent Test**:
```bash
# Test default
python src/server.py
curl http://localhost:8000/health | jq '.personality_variant'
# Expected: "default"

# Test variant2
VENOM_PERSONALITY=variant2 python src/server.py
curl http://localhost:8000/health | jq '.personality_variant'
# Expected: "variant2"

# Test invalid
VENOM_PERSONALITY=invalid python src/server.py
# Expected: Warning in logs, fallback to "default"

# A/B test:
# Run same interactions on both variants, compare tone and behavior
```

---

## Phase 8: User Story 6 - Zero-Cost Deployment & Operation (P3)

**Story Goal**: Deploy to Azure Container Apps with scale-to-zero within free tier limits

**Independent Test Criteria**:
- ✅ Docker image builds successfully
- ✅ Container runs locally and passes health check
- ✅ Embedding model included in image (no runtime download)
- ✅ Azure Container App deploys successfully
- ✅ Persistent volume mounted for ChromaDB data
- ✅ Public HTTPS endpoint accessible
- ✅ Container scales to zero when idle
- ✅ Container wakes in <2s on new request

**Tasks**:
- [ ] T053 [US6] Create Dockerfile with python:3.11-slim base, multi-stage if needed
- [ ] T054 [US6] Add sentence-transformers model pre-download to Dockerfile (cache during build)
- [ ] T055 [US6] Add COPY commands for src/, venom_personality*.md, requirements.txt to Dockerfile
- [ ] T056 [US6] Set WORKDIR /app, expose port 8000, add CMD for uvicorn in Dockerfile
- [ ] T057 [US6] Build Docker image locally: docker build -t symbiote-mcp:latest .
- [ ] T058 [US6] Test Docker container locally: docker run with volume mount, verify health endpoint
- [ ] T059 [US6] Create deployment/azure-deploy.sh script with Azure CLI commands
- [ ] T060 [US6] Add Azure resource group creation to deploy script
- [ ] T061 [US6] Add Azure Container Registry creation and image push to deploy script
- [ ] T062 [US6] Add Container Apps environment creation to deploy script
- [ ] T063 [US6] Add persistent storage setup to deploy script (Azure Files)
- [ ] T064 [US6] Add Container App creation to deploy script (CPU: 0.5, Memory: 1GB, min replicas: 0, max: 1)
- [ ] T065 [US6] Add environment variables to Container App deployment (PORT, CHROMADB_PATH, etc.)
- [ ] T066 [US6] Deploy to Azure: run deployment script
- [ ] T067 [US6] Test Azure deployment: curl health endpoint, verify response
- [ ] T068 [US6] Test scale-to-zero: wait for idle period, verify container scales down
- [ ] T069 [US6] Test wake-up: send request after scale-down, verify <2s wake time
- [ ] T070 [US6] Monitor Azure costs: verify staying within free tier limits

**Dependencies**: Requires Phase 5 (US3 MVP complete)

**Parallel Opportunities**: T059-T065 (script preparation can happen while testing Docker locally)

**Independent Test**:
```bash
# Local Docker test
docker build -t symbiote-mcp:latest .
docker run -p 8000:8000 -v $(pwd)/data:/app/data symbiote-mcp:latest
curl http://localhost:8000/health

# Azure deployment
cd deployment
./azure-deploy.sh

# Test deployed app
curl https://symbiote-mcp.<random>.azurecontainerapps.io/health

# Verify costs in Azure portal
# Expected: $0/month (within free tier)
```

---

## Phase 9: Polish & Cross-Cutting Concerns

**Goal**: Production-ready polish, documentation, and final verification

**Tasks**:
- [ ] T071 Add comprehensive error handling throughout src/server.py (catch exceptions, return proper error responses)
- [ ] T072 [P] Add logging throughout codebase (startup, memory operations, errors) using Python logging module
- [ ] T073 [P] Add input sanitization for user content (escape special characters, prevent injection)
- [ ] T074 [P] Update README.md with complete setup instructions, deployment guide, and usage examples
- [ ] T075 [P] Create tests/manual_testing.md with comprehensive test scenarios for all user stories
- [ ] T076 Verify all environment variables documented in .env.example and README
- [ ] T077 [P] Add docker-compose.yml for local development (optional convenience)
- [ ] T078 Run full integration test: store memory → restart → search memory → verify persistence
- [ ] T079 Run cross-platform test: same memory accessible from Claude web, mobile, ChatGPT
- [ ] T080 Performance test: verify search <500ms, storage <1s for typical content
- [ ] T081 Validate constitutional compliance: review all 10 non-negotiable rules satisfied
- [ ] T082 Final code review: verify all functions have type hints, docstrings, and error handling

**Parallel Opportunities**: T072-T077 (documentation and logging tasks)

**Validation**:
```bash
# Full test suite
./tests/run-manual-tests.sh

# Expected:
# ✅ All user stories pass independent tests
# ✅ Performance targets met
# ✅ Constitutional compliance verified
# ✅ Production deployment successful
```

---

## Task Summary by User Story

| User Story | Priority | Task Count | Task IDs | MVP |
|------------|----------|------------|----------|-----|
| Setup | - | 10 | T001-T010 | ✅ |
| Foundational | - | 5 | T011-T015 | ✅ |
| US1: Cross-Platform Memory | P1 | 7 | T016-T022 | ✅ |
| US2: Semantic Memory | P1 | 10 | T023-T032 | ✅ |
| US3: Mandatory Protocol | P1 | 6 | T033-T038 | ✅ |
| **MVP Complete** | **-** | **38** | **T001-T038** | **✅** |
| US4: Consistent Personality | P2 | 5 | T039-T043 | ❌ |
| US5: Personality Experiments | P2 | 9 | T044-T052 | ❌ |
| US6: Zero-Cost Deployment | P3 | 18 | T053-T070 | ❌ |
| Polish | - | 12 | T071-T082 | ❌ |
| **Total** | **-** | **82** | **T001-T082** | **-** |

---

## Parallel Execution Examples

### Phase 1 (Setup)
```bash
# Can run in parallel (4 agents)
Agent 1: T002 (requirements.txt)
Agent 2: T003 (.gitignore)
Agent 3: T004 (.env.example)
Agent 4: T005 (README.md)

# Then in parallel (4 agents)
Agent 1: T007 (memory/__init__.py)
Agent 2: T008 (prompts/__init__.py)
Agent 3: T009 (manual_testing.md)
Agent 4: T010 (docs/learning/)
```

### Phase 3 (US1)
```bash
# Sequential: T016, T017 (server setup)

# Then in parallel (2 agents)
Agent 1: T018 (list_prompts handler)
Agent 2: T019 (list_tools handler)

# Sequential: T020-T022 (health check, startup, test)
```

### Phase 4 (US2)
```bash
# Sequential: T023-T025 (store_memory)

# Then in parallel (3 agents)
Agent 1: T026 (search_memory handler)
Agent 2: T027 (search logic)
Agent 3: T028 (search validation)

# Sequential: T029-T032 (conversion, tests)
```

---

## Notes

### Test Strategy
- **Manual testing only** per constitution
- Each phase has independent test criteria
- Use MCP clients (Claude Desktop, ChatGPT) for end-to-end validation
- Document test scenarios in tests/manual_testing.md

### Learning Documentation
- Follow ai_agent_learning_protocol.md for each component
- Generate design doc BEFORE implementation
- Generate implementation doc AFTER coding
- Maintain decision log DURING development
- See docs/learning/ for structure

### Constitutional Compliance
- All tasks use Python 3.11+ with async/await
- Type hints required for all functions
- No paid APIs (sentence-transformers is free/local)
- Simple over clever (embedded ChromaDB, env var config)
- Educational value in every choice

### Performance Targets
- Memory search: <500ms (T080 validates)
- Memory storage: <1s (T080 validates)
- Container cold start: <10s (T058 validates)
- Scale-zero wake: <2s (T069 validates)

### Cost Constraints
- Must stay in Azure free tier
- 180,000 vCPU-seconds/month limit
- Target: $0-2/month operational cost
- T070 validates cost compliance

---

**Ready to implement! Start with Phase 1 (T001-T010) for MVP foundation.**
