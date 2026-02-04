# MCP Prompts System - Implementation

## Code Overview

**File:** `src/prompts/venom.py`
**Lines of Code:** ~55
**Dependencies:** pathlib (standard library)

## Key Sections

### Class Definition

```python
class VenomPrompt:
    def __init__(self, personality_file_path: Path) -> None:
        self.personality_file_path = personality_file_path
        self._content: str | None = None
```

**What This Does:** Stores file path, prepares for lazy loading (content starts as None).

### Lazy File Loading

```python
def _load_content(self) -> str:
    if self._content is None:
        if not self.personality_file_path.exists():
            raise FileNotFoundError(f"Personality file not found: {self.personality_file_path}")
        
        self._content = self.personality_file_path.read_text(encoding="utf-8")
        print(f"Loaded personality from: {self.personality_file_path.name}")
    
    return self._content
```

**What This Does:** Loads file only when first needed, caches for future calls.

**Line-by-Line:**
- `if self._content is None`: Check if already loaded
- `.exists()`: Verify file exists before reading
- `.read_text(encoding="utf-8")`: Read entire file as string
- Cache in `self._content`: Subsequent calls return cached value

### Get MCP Prompt

```python
def get_prompt(self) -> Dict[str, Any]:
    content = self._load_content()
    
    return {
        "name": "venom_identity",
        "description": "Venom symbiote personality with mandatory memory protocol",
        "content": content,
    }
```

**What This Does:** Returns MCP-formatted prompt dict.

## Key Takeaways

1. **Lazy loading optimizes startup**: File read only when needed
2. **Caching prevents redundant I/O**: Read once, reuse many times
3. **Fail fast on missing files**: Better to crash at startup than serve broken prompts
4. **Pathlib is cleaner**: Path objects better than string manipulation
5. **UTF-8 encoding explicit**: Handles international characters correctly
