# MCP Prompts System - Decisions Log

## Decision 1: Lazy Loading vs Eager Loading

**Context:** When to read personality file?

**Decision:** Lazy load (read on first use)

**Reasoning:**
- Consistent with embedding service pattern
- Fast object creation
- Server startup triggers load anyway (via lifespan)

**Trade-offs:**
- ✅ Gained: Flexibility, standard pattern
- ❌ Lost: Nothing (lifespan triggers load)

## Decision 2: Cache File Content

**Context:** Should we re-read file on each prompt request?

**Decision:** Cache content after first read

**Reasoning:**
- Personality file changes rarely
- Reading file 1000x wastes I/O
- Can restart server if file changes

**Trade-offs:**
- ✅ Gained: Performance (file I/O → memory access)
- ❌ Lost: Live reloading (acceptable, restart is fine)

## Problem 1: Wrong File Path

**What Happened:** FileNotFoundError when loading personality

**Why:** Used relative path, wrong working directory

**Solution:** Use absolute path from config:
```python
Path(__file__).parent.parent / "venom_personality.md"
```

**Lesson:** Always use absolute paths or resolve relative to known location
