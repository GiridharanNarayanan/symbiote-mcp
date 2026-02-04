# MCP Prompts System - Design

## What We're Building

A simple file loader that reads the Venom personality from markdown files and exposes it as an MCP prompt. Supports multiple personality variants via environment variable selection.

**Location:** `src/prompts/venom.py`

**Dependencies:** pathlib (standard library), config

**Used by:** MCP server (get_prompt handler)

## Architecture

```
VenomPrompt
  ↓
Read personality file (lazy load)
  - venom_personality.md (default variant)
  - venom_personality_v2.md (variant2)
  ↓
Return as MCP prompt
  ↓
Client receives personality text
  ↓
Injects into LLM system context
```

## Why This Design?

### Technology Choice: File-based vs Hardcoded

**Alternatives Considered:**

1. **Hardcoded string in Python**
   - **Pros:** No file I/O, faster
   - **Cons:** Can't update without code change, violates constitution
   - **Why rejected:** Constitution requires personality from file

2. **Database storage**
   - **Pros:** Versioning, multiple personalities
   - **Cons:** Overkill, adds complexity
   - **Why rejected:** File is simpler for static content

3. **File-based (chosen)**
   - **Pros:** Easy to edit, no code changes, supports variants
   - **Cons:** File I/O overhead (minimal)
   - **Why chosen:** Constitution requirement, simplicity

### Key Concepts

#### Concept 1: MCP Prompts vs Tools

**MCP Prompts:**
- Static text injected into LLM context
- Like system messages
- Define behavior/personality
- Example: Venom personality

**MCP Tools:**
- Functions the LLM can call
- Dynamic, take parameters
- Return results
- Example: search_memory, store_memory

#### Concept 2: Personality Variants

Multiple personality files for experimentation:
- `default`: venom_personality.md (friendly, witty)
- `variant2`: venom_personality_v2.md (lethal protector, dominant)

Switch via environment variable, no code changes.

## How It Works

**Load Prompt:**
1. Config determines variant (`VENOM_PERSONALITY=variant2`)
2. Map variant to file path
3. Read file content (cached)
4. Return as MCP prompt object

**Client Uses:**
1. Client requests `venom_identity` prompt
2. Server returns personality content
3. Client injects into system context
4. LLM follows personality instructions

## Edge Cases

| Scenario | How We Handle It |
|----------|------------------|
| **File not found** | Raise FileNotFoundError on startup |
| **Invalid variant** | Fall back to default, warn in logs |
| **File read error** | Fail fast, don't serve broken prompt |

## What You'll Learn

- [ ] Difference between MCP prompts and tools
- [ ] Why file-based configuration is flexible
- [ ] Lazy loading pattern for file I/O
- [ ] Environment variable-based feature flags

## Design Decisions

**Key Decision:** File-based vs database
- **Trade-off:** No versioning, but much simpler
- **Why:** Static content, version control via git
