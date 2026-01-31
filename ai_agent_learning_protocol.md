# AI Agent Learning Protocol - Venom MCP Implementation

**Instructions for Claude Code, GitHub Copilot, and other AI coding assistants**

---

## Core Directive

As you implement each component of the Venom MCP Server, you MUST automatically generate comprehensive learning documentation. The goal is to teach the concepts, not just build the code.

## Documentation Requirements for EVERY Implementation Step

### Before Writing Any Code

Generate a file: `docs/learning/[component-name]-design.md`

**Must include:**

1. **What We're Building**
   - Component purpose in 2-3 sentences
   - Where it fits in the overall architecture
   - ASCII diagram showing connections

2. **Why We're Building It This Way**
   - Technology choice rationale
   - Alternative approaches considered and rejected
   - Trade-offs made

3. **Key Concepts to Understand**
   - List 3-5 concepts needed to understand this component
   - For each concept:
     - Simple definition (ELI5 style)
     - Why it matters here
     - Link to deeper learning resource

4. **Design Decisions**
   - Data structures chosen and why
   - Algorithms chosen and why
   - Patterns used (with simple explanations)

5. **Expected Behavior**
   - Input → Process → Output flow
   - Edge cases and how we handle them
   - Error scenarios

6. **Learning Goals**
   - What the developer should understand after implementing this
   - Skills being practiced
   - Concepts being reinforced

### After Writing Code

Generate a file: `docs/learning/[component-name]-implementation.md`

**Must include:**

1. **Code Walkthrough**
   - Line-by-line explanation of key sections
   - Why each part exists
   - What would break if we removed it

2. **How It Works (Step-by-Step)**
   - Request/data flow numbered steps
   - State changes at each step
   - What happens in memory

3. **Integration Points**
   - How this component connects to others
   - What it depends on
   - What depends on it

4. **Testing Strategy**
   - How to manually test this component
   - What outputs to expect
   - Common failure modes and how to debug

5. **Key Takeaways**
   - 3-5 bullet points of what was learned
   - Patterns that can be reused elsewhere
   - Gotchas to remember

6. **Going Deeper**
   - Related concepts to explore
   - Resources for deeper understanding
   - Optional improvements to consider

### During Implementation

Generate a file: `docs/learning/[component-name]-decisions.md`

**Document in real-time:**

1. **Decision Log**
   ```
   [Timestamp] Decision: [What was decided]
   Context: [Why this decision point arose]
   Options: [What alternatives were considered]
   Choice: [What we chose]
   Reasoning: [Why we chose this]
   Trade-offs: [What we gained/lost]
   ```

2. **Problems Encountered**
   ```
   [Problem]: [Description]
   [Attempted Solution 1]: [What was tried and result]
   [Attempted Solution 2]: [What was tried and result]
   [Final Solution]: [What worked and why]
   [Lesson Learned]: [Key takeaway]
   ```

3. **Code Evolution**
   - Show how code changed from first version to final
   - Explain why each refactoring happened
   - What improvement each change brought

---

## Specific Documentation for Venom Components

### 1. MCP Server Setup (`src/server.py`)

**Pre-Implementation Doc: `docs/learning/mcp-server-design.md`**

Must explain:
- What is the MCP protocol? (Simple explanation)
- Why FastAPI for this? (vs Flask, vs pure Python)
- What is SSE and why do we need it?
- How does async/await work in Python?
- What is an ASGI server?

**Post-Implementation Doc: `docs/learning/mcp-server-implementation.md`**

Must explain:
- Request lifecycle from client to server
- How FastAPI routes work
- How MCP handlers are registered
- What happens when a tool is called
- How async functions execute

### 2. Embeddings System (`src/memory/embeddings.py`)

**Pre-Implementation Doc: `docs/learning/embeddings-design.md`**

Must explain:
- What are embeddings? (Simple metaphor)
- How do they represent meaning?
- What is a vector? What is 384 dimensions?
- Why sentence-transformers?
- What is all-MiniLM-L6-v2?

**Post-Implementation Doc: `docs/learning/embeddings-implementation.md`**

Must explain:
- How text becomes a vector (step-by-step)
- What the model is doing internally
- Why we cache the model globally
- What .encode() actually does
- How to interpret embedding values

### 3. ChromaDB Storage (`src/memory/store.py`)

**Pre-Implementation Doc: `docs/learning/chromadb-design.md`**

Must explain:
- What is a vector database?
- How is it different from SQL/NoSQL?
- What is cosine similarity?
- How does semantic search work?
- Why embedded vs server mode?

**Post-Implementation Doc: `docs/learning/chromadb-implementation.md`**

Must explain:
- How ChromaDB stores vectors on disk
- The search algorithm (cosine similarity math)
- Why we convert distance to relevance
- How collections work
- What happens during .query()

### 4. Venom Prompt Loading (`src/prompts/venom.py`)

**Pre-Implementation Doc: `docs/learning/mcp-prompts-design.md`**

Must explain:
- What are MCP prompts?
- How do they differ from tools?
- Why load personality from file?
- How does the client receive it?
- When does it get injected?

**Post-Implementation Doc: `docs/learning/mcp-prompts-implementation.md`**

Must explain:
- The prompt request/response flow
- How file reading works
- Error handling for missing files
- How the text becomes system context
- Why this approach vs hardcoding

### 5. Docker Containerization (`Dockerfile`)

**Pre-Implementation Doc: `docs/learning/docker-design.md`**

Must explain:
- What is a container? (Simple metaphor)
- Why Docker for this project?
- Multi-stage builds concept
- Why pre-download the model?
- What is the difference between image and container?

**Post-Implementation Doc: `docs/learning/docker-implementation.md`**

Must explain:
- Each Dockerfile instruction purpose
- Build process step-by-step
- Layer caching concept
- Why slim base image?
- How CMD gets executed

### 6. Azure Deployment (`deployment/azure-deploy.sh`)

**Pre-Implementation Doc: `docs/learning/azure-containerApps-design.md`**

Must explain:
- What is Azure Container Apps?
- How is it different from Functions/VMs?
- What is scale-to-zero?
- How do persistent volumes work?
- What is an environment vs app?

**Post-Implementation Doc: `docs/learning/azure-containerApps-implementation.md`**

Must explain:
- Each Azure CLI command purpose
- Resource hierarchy (subscription→group→environment→app)
- How environment variables pass to container
- How persistent volumes get mounted
- How ingress/networking works

---

## Documentation Structure

```
venom-mcp/
├── docs/
│   ├── learning/
│   │   ├── 00-overview.md                    # Project architecture overview
│   │   │
│   │   ├── 01-mcp-server-design.md
│   │   ├── 01-mcp-server-implementation.md
│   │   ├── 01-mcp-server-decisions.md
│   │   │
│   │   ├── 02-embeddings-design.md
│   │   ├── 02-embeddings-implementation.md
│   │   ├── 02-embeddings-decisions.md
│   │   │
│   │   ├── 03-chromadb-design.md
│   │   ├── 03-chromadb-implementation.md
│   │   ├── 03-chromadb-decisions.md
│   │   │
│   │   ├── 04-mcp-prompts-design.md
│   │   ├── 04-mcp-prompts-implementation.md
│   │   ├── 04-mcp-prompts-decisions.md
│   │   │
│   │   ├── 05-docker-design.md
│   │   ├── 05-docker-implementation.md
│   │   ├── 05-docker-decisions.md
│   │   │
│   │   ├── 06-azure-deployment-design.md
│   │   ├── 06-azure-deployment-implementation.md
│   │   ├── 06-azure-deployment-decisions.md
│   │   │
│   │   └── 99-glossary.md                    # All terms explained simply
│   │
│   └── diagrams/                              # Visual learning aids
│       ├── architecture-overview.txt          # ASCII diagram
│       ├── request-flow.txt
│       ├── memory-search-flow.txt
│       └── deployment-topology.txt
```

---

## Writing Style Requirements

### Use Simple Language
- ❌ "The ASGI server instantiates the application context"
- ✅ "The ASGI server creates a new copy of your app for each request"

### Use Metaphors
- ❌ "Vector embeddings represent semantic relationships in n-dimensional space"
- ✅ "Think of embeddings like GPS coordinates. Words with similar meanings are 'close together' in this space, even if they use different letters"

### Show Examples
For every concept, show:
1. Code example (small, focused)
2. What it does (plain English)
3. What changes if you modify it

### Use Visuals
```
# Good: ASCII diagrams

User Message
     ↓
search_memory()
     ↓
Generate Embedding [0.123, -0.456, ...]
     ↓
ChromaDB Query
     ↓
Find Similar Vectors (cosine similarity)
     ↓
Return Top 5 Matches
     ↓
Format Results
     ↓
Response to User
```

### Answer "Why?" 3 Levels Deep

**Level 1:** Why this component?
- "We need embeddings to search by meaning, not keywords"

**Level 2:** Why this approach?
- "We use sentence-transformers because it's free and runs locally"

**Level 3:** Why does that matter?
- "Running locally means no API costs, no rate limits, and works offline"

---

## Learning Documentation Templates

### Template: Design Document

```markdown
# [Component Name] - Design

## What We're Building

[2-3 sentence description]

## Architecture Diagram

```
[ASCII diagram showing this component's place]
```

## Why This Design?

### Technology Choice: [Technology Name]
**Alternatives Considered:**
- Option A: [Why rejected]
- Option B: [Why rejected]

**Why We Chose [Technology Name]:**
1. Reason 1
2. Reason 2
3. Reason 3

### Key Concepts

#### Concept 1: [Name]
- **Simple Explanation:** [ELI5]
- **Why It Matters:** [Relevance to this component]
- **Learn More:** [Link or reference]

#### Concept 2: [Name]
- **Simple Explanation:** [ELI5]
- **Why It Matters:** [Relevance to this component]
- **Learn More:** [Link or reference]

## How It Works

### Input
[What comes in]

### Process
1. Step 1: [Description]
2. Step 2: [Description]
3. Step 3: [Description]

### Output
[What goes out]

## Edge Cases

| Scenario | How We Handle It |
|----------|------------------|
| [Case 1] | [Solution]       |
| [Case 2] | [Solution]       |

## What You'll Learn

After implementing this component, you should understand:
- [ ] Concept 1
- [ ] Concept 2
- [ ] Concept 3
```

### Template: Implementation Document

```markdown
# [Component Name] - Implementation Walkthrough

## Code Overview

File: `[path/to/file.py]`
Lines of Code: [X]
External Dependencies: [Y]

## Key Code Sections

### Section 1: [Name]

```python
[Code snippet]
```

**What This Does:**
[Plain English explanation]

**Line-by-Line:**
- Line X: [Why this line exists]
- Line Y: [What happens here]
- Line Z: [Why we do it this way]

**What Would Break:**
If we removed this, [consequence]

### Section 2: [Name]
[Same format]

## Request Flow Example

### Example: [Use Case]

**Input:**
```python
[Example input]
```

**Step-by-Step Execution:**
1. Function `[name]` is called
   - State: [What's in memory]
   - Action: [What happens]
   
2. [Next function/operation]
   - State: [Changes]
   - Action: [What happens]
   
3. [Final step]
   - State: [Final state]
   - Returns: [Output]

**Output:**
```python
[Example output]
```

## How to Test

### Manual Test 1: [Scenario]
```bash
# Run this command
[command]

# Expected output
[output]

# What it proves
[explanation]
```

### Manual Test 2: [Scenario]
[Same format]

## Integration

### Dependencies (What This Needs)
- Component A: [How it's used]
- Component B: [How it's used]

### Dependents (What Needs This)
- Component C: [How it uses this]
- Component D: [How it uses this]

## Key Takeaways

1. **[Concept]**: [What you learned about it]
2. **[Pattern]**: [When to use it again]
3. **[Gotcha]**: [What to watch out for]

## Going Deeper

**Related Concepts:**
- [Topic 1]: [Resource/link]
- [Topic 2]: [Resource/link]

**Optional Improvements:**
- [Enhancement 1]: [What it would add]
- [Enhancement 2]: [What it would add]
```

### Template: Decision Log

```markdown
# [Component Name] - Decisions Log

## Decision 1: [Topic]

**Context:**
[Why this decision point arose]

**Options Considered:**

### Option A: [Name]
- **Pros:** [List]
- **Cons:** [List]
- **Example:** [Code/command]

### Option B: [Name]
- **Pros:** [List]
- **Cons:** [List]
- **Example:** [Code/command]

**Decision: We chose [Option X]**

**Reasoning:**
1. [Reason]
2. [Reason]
3. [Reason]

**Trade-offs:**
- ✅ We gained: [Benefits]
- ❌ We lost: [Drawbacks]

**Timestamp:** [When decided]

---

## Problem 1: [Description]

**What Happened:**
[Error or issue description]

**Why It Happened:**
[Root cause]

**Attempted Solutions:**

1. **Try:** [What we tried]
   - **Result:** [What happened]
   - **Why It Didn't Work:** [Explanation]

2. **Try:** [Next attempt]
   - **Result:** [What happened]
   - **Why It Didn't Work:** [Explanation]

**Final Solution:**
[What worked]

**Why This Worked:**
[Explanation]

**Lesson Learned:**
[Key takeaway for future]

**Timestamp:** [When solved]
```

---

## AI Agent Execution Protocol

### When Implementing a Component:

```
1. ✅ Create design doc FIRST (docs/learning/XX-component-design.md)
2. ✅ Start decision log (docs/learning/XX-component-decisions.md)
3. ✅ Write code with inline educational comments
4. ✅ Update decision log with real-time decisions
5. ✅ Create implementation doc AFTER (docs/learning/XX-component-implementation.md)
6. ✅ Update main overview doc with new component
7. ✅ Add new terms to glossary
```

### Comment Style in Code:

```python
# ❌ BAD COMMENT (what, not why)
# Get the embedding model
model = get_embedding_model()

# ✅ GOOD COMMENT (why, how it works)
# Load the pre-trained model into memory (only once via global cache).
# This avoids re-loading the 80MB model file on every request.
# The model converts text into 384-dimensional vectors representing meaning.
model = get_embedding_model()
```

### Inline Learning Annotations:

```python
def search_memories(query: str, limit: int = 5) -> List[Memory]:
    """
    Search memories using semantic similarity.
    
    LEARNING NOTE:
    - 'Semantic' means searching by MEANING, not keywords
    - We convert the query to a vector (list of 384 numbers)
    - ChromaDB finds vectors that are "close" to the query vector
    - "Close" is measured using cosine similarity (math explained in docs)
    
    Args:
        query: Plain English question (e.g., "coding preferences")
        limit: Max results to return
        
    Returns:
        List of Memory objects, sorted by relevance (best first)
        
    Example:
        >>> search_memories("What languages do I prefer?", limit=3)
        [Memory(content="Prefers TypeScript", relevance=0.89), ...]
    """
    # Implementation here...
```

---

## Verification Checklist

Before marking a component complete, verify:

- [ ] Design doc exists and explains WHY
- [ ] Implementation doc exists and explains HOW
- [ ] Decision log exists and shows real decisions made
- [ ] Code has educational inline comments
- [ ] At least one ASCII diagram exists
- [ ] Examples are included for all key functions
- [ ] Glossary is updated with new terms
- [ ] Manual test cases are documented
- [ ] "Key Takeaways" section exists
- [ ] "Going Deeper" resources are provided

---

## Example: Complete Documentation Set

### `docs/learning/02-embeddings-design.md`

```markdown
# Embeddings System - Design

## What We're Building

A system that converts text into numerical vectors (lists of numbers) that represent the meaning of the text. This lets us compare how similar two pieces of text are, even if they use completely different words.

## Architecture Diagram

```
User Text: "I prefer TypeScript"
         ↓
    Tokenization (split into words)
         ↓
    BERT Model (sentence-transformers)
         ↓
    384 Numbers: [0.234, -0.567, 0.123, ...]
         ↓
    Stored in ChromaDB
```

## Why This Design?

### Technology Choice: sentence-transformers

**Alternatives Considered:**
- **OpenAI Embeddings API**: Rejected because costs $0.0001 per 1K tokens, adds dependency
- **Word2Vec**: Rejected because less accurate for sentences, older technology
- **Custom BERT fine-tuning**: Rejected because overkill, requires ML expertise

**Why We Chose sentence-transformers:**
1. **Free and local** - Runs on your computer, no API calls
2. **Good enough quality** - 384 dimensions capture meaning well for personal use
3. **Easy to use** - One function call: `model.encode(text)`
4. **Industry standard** - Used by many production systems

### Key Concepts

#### Concept 1: Vector Embeddings

**Simple Explanation:**
Imagine every word/sentence has a location in a huge space (like GPS coordinates, but with 384 dimensions instead of 2). Words with similar meanings are located near each other.

For example:
- "TypeScript" and "JavaScript" are close together
- "TypeScript" and "banana" are far apart

**Why It Matters:**
We can search by MEANING instead of exact keywords. If you stored "I like TypeScript" and search for "What languages do I prefer?", the system finds it even though the words don't match.

**Learn More:**
- Visual explanation: https://jalammar.github.io/illustrated-word2vec/
- Deep dive: https://www.sbert.net/

#### Concept 2: 384 Dimensions

**Simple Explanation:**
A "dimension" is just a number in the list. Our embeddings are lists of 384 numbers. Each number represents a different aspect of meaning (like "is it a programming language?", "is it technical?", "is it positive?").

```python
# Example embedding (simplified to 5 dimensions)
"TypeScript" → [0.8, 0.3, -0.1, 0.5, 0.2]
                 ↑    ↑    ↑    ↑    ↑
                 │    │    │    │    └─ (unknown aspect)
                 │    │    │    └────── (some aspect)
                 │    │    └─────────── (some aspect)  
                 │    └──────────────── (some aspect)
                 └───────────────────── "programming-ness"
```

**Why It Matters:**
More dimensions = more nuance captured. 384 is a sweet spot: enough to capture complex meanings, small enough to be fast.

**Learn More:**
- Dimensionality: https://www.pinecone.io/learn/vector-embeddings/

## How It Works

### Input
```python
text = "I prefer TypeScript over JavaScript"
```

### Process
1. **Tokenization**: Split text into words/sub-words
   - "I", "prefer", "Type", "##Script", "over", "Java", "##Script"
   
2. **Model Processing**: Feed tokens through neural network
   - Each token gets a vector
   - Vectors are combined (averaged) into one sentence vector
   
3. **Output**: 384-dimensional vector
   - One number for each dimension
   - Numbers range from about -1 to +1

### Output
```python
embedding = [0.234, -0.567, 0.123, ..., 0.089]  # 384 numbers total
```

## Edge Cases

| Scenario | How We Handle It |
|----------|------------------|
| Empty string | Return zero vector (all zeros) |
| Very long text (>512 words) | Truncate to 512 words (model limit) |
| Non-English text | Works okay (model is multilingual) |
| Special characters/code | Handles reasonably (model trained on varied text) |

## What You'll Learn

After implementing this component, you should understand:
- [ ] What embeddings are and why they're useful
- [ ] How text becomes numbers
- [ ] Why we use pre-trained models
- [ ] What "semantic similarity" means
- [ ] How to cache expensive operations in Python
```

---

## Summary for AI Agents

**Your job is not just to write code. Your job is to TEACH while you build.**

Every component you implement should leave the developer understanding:
1. **What** was built
2. **Why** it was built this way
3. **How** it works internally
4. **When** to use similar patterns again
5. **What** to explore next

Generate documentation AUTOMATICALLY. Don't wait to be asked. Make learning effortless.
