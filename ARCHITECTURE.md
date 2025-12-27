# System Architecture

## Overview

The Multi-Agent Debate System is designed with a modular, layered architecture that separates concerns and enables independent testing and scaling.

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer (Click)                       │
│   (debate, debates list, debates view, debates export)     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              Orchestration Layer                            │
│  (DebateOrchestrator: run_debate, get_debate, list_debates)│
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐  ┌──────▼────────┐  ┌─────▼──────────┐
│ Agent Layer    │  │ Storage Layer │  │ Utils Layer    │
│                │  │               │  │                │
│ • ClaudeAgent  │  │ JSON Backend  │  │ • Formatting   │
│ • GeminiAgent  │  │ • save_debate │  │ • Validation   │
│ • create_agent │  │ • get_debate  │  │ • Prompt build │
└───────┬────────┘  │ • list_debates│  │ • Estimation   │
        │           │ • delete_deb. │  └────────────────┘
        │           └────────┬──────┘
        │                    │
        └────────────┬───────┘
                     │
        ┌────────────▼──────────────┐
        │   Data Models Layer       │
        │   (Pydantic Models)       │
        │                           │
        │ • AgentConfig             │
        │ • DebateTopic             │
        │ • AgentResponse           │
        │ • DebateRecord            │
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────┐
        │   External CLIs           │
        │                           │
        │ • Claude CLI              │
        │ • Gemini CLI              │
        └───────────────────────────┘
```

---

## Layer Details

### 1. CLI Layer (`src/cli.py`)

**Purpose:** User interface - handles all command-line interactions

**Components:**
- `cli_group`: Main Click group
- `debate_command`: Run a new debate
- `debates_group`: Group for debate management
- `debates_list_command`: List stored debates
- `debates_view_command`: View debate details
- `debates_export_command`: Export to file

**Responsibilities:**
- Parse command-line arguments
- Validate user input
- Call orchestrator methods
- Format and display output
- Handle errors gracefully

**Flow:**
```
User Input → Click Command → Orchestrator → Display Output
```

---

### 2. Orchestration Layer (`src/orchestrator.py`)

**Purpose:** Central logic - orchestrates the debate execution flow

**Main Class:** `DebateOrchestrator`

**Methods:**
- `run_debate(topic, agents_config)`: Execute debate with context-passing
- `get_debate(debate_id)`: Retrieve stored debate
- `list_debates(limit)`: List stored debates

**Key Functions:**
- `build_for_prompt(topic)`: Build FOR agent prompt
- `build_against_prompt(topic, for_response)`: Build AGAINST prompt
- `build_synthesis_prompt(topic, for_response, against_response)`: Build SYNTHESIS prompt

**Execution Flow (Context-Passing):**
```
1. FOR Agent receives: topic
   └─> Returns: FOR_response

2. AGAINST Agent receives: topic + FOR_response
   └─> Returns: AGAINST_response

3. SYNTHESIS Agent receives: topic + FOR_response + AGAINST_response
   └─> Returns: SYNTHESIS_response

4. Store all responses in DebateRecord
5. Return complete debate record
```

**Key Feature:** Sequential execution ensures context-passing at each step

---

### 3. Agent Layer (`src/agents.py`)

**Purpose:** Subprocess execution - manages CLI tool communication

**Classes:**

#### Base Class: `Agent`
- Abstract base for all agents
- Manages subprocess execution
- Handles timeouts and errors
- Parses CLI output

#### `ClaudeAgent(Agent)`
- Executes: `claude --model {model_id} --print "{prompt}"`
- Returns: `AgentResponse` with stdout

#### `GeminiAgent(Agent)`
- Executes: `gemini --yolo -m {model_id} "{prompt}"`
- Cleans: Removes "Loaded cached credentials" lines
- Returns: Clean `AgentResponse`

#### `create_agent(config)` Factory
- Maps `AgentConfig` to agent instance
- Handles unknown providers with error

**Subprocess Details:**
```python
asyncio.create_subprocess_exec(
    *command,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
    timeout=config.timeout_seconds
)
```

**Error Handling:**
- `TimeoutError`: CLI didn't respond in time
- `FileNotFoundError`: CLI not installed
- `Exception`: Any other error
All return graceful `AgentResponse` with error info

---

### 4. Storage Layer (`src/storage.py`)

**Purpose:** Persistence - manages debate record storage

**Base Class:** `StorageBackend` (abstract)
- `save_debate(debate) → debate_id`
- `get_debate(debate_id) → DebateRecord`
- `list_debates(limit) → List[DebateRecord]`
- `delete_debate(debate_id) → bool`

**Implementation:** `JSONStorageBackend`

**File Structure:**
```
data/debates/
├── 550e8400-e29b-41d4-a716-446655440000.json
│   {
│     "debate_id": "550e8400-e29b-41d4-a716-446655440000",
│     "topic": { "title": "...", "description": "..." },
│     "agents_config": [...],
│     "agent_responses": [...],
│     "total_execution_time_ms": 6250.9,
│     "created_at": "2025-01-15T18:30:45"
│   }
├── f47ac10b-58cc-4372-a567-0e02b2c3d479.json
└── _index.json
    [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2025-01-15T18:30:45",
        "topic_title": "Should AI have rights?"
      },
      ...
    ]
```

**Index Benefits:**
- Fast lookups without reading all JSON files
- Support for pagination (`list_debates`)
- Quick validation of debate existence

---

### 5. Data Models Layer (`src/models.py`)

**Purpose:** Type safety - defines all data structures

**Models:** (Pydantic v2)

#### `AgentConfig`
```python
- name: str
- role: Literal["FOR", "AGAINST", "SYNTHESIS"]
- model_provider: Literal["claude", "gemini"]
- model_name: str (e.g., "haiku", "sonnet")
- model_id: str (auto-generated: "claude-haiku-4-5-20251001")
- temperature: float (0.0-1.0, default 0.7)
- max_tokens: int (default 2000)
- timeout_seconds: int (default 60)
```

**Auto Model ID Generation:**
- `claude + haiku` → `claude-haiku-4-5-20251001`
- `gemini + flash-lite` → `gemini-2.5-flash-lite`
- Uses `model_post_init()` hook

#### `DebateTopic`
```python
- title: str
- description: str
```

#### `AgentResponse`
```python
- agent_name: str
- role: Literal["FOR", "AGAINST", "SYNTHESIS"]
- model_provider: str
- model_name: str
- response_text: str
- execution_time_ms: float
- success: bool
- error_message: Optional[str]
```

#### `DebateRecord`
```python
- debate_id: str (UUID, auto-generated)
- topic: DebateTopic
- agents_config: List[AgentConfig]
- agent_responses: List[AgentResponse]
- total_execution_time_ms: float
- created_at: datetime (auto-generated)
```

**Benefits of Pydantic:**
- Automatic validation
- Type hints
- JSON serialization
- Clear error messages
- IDE autocomplete support

---

### 6. Utils Layer (`src/utils.py`)

**Purpose:** Reusable functions - formatting and helpers

**Formatting Functions:**
- `format_debate_for_display(debate)` → Plain text
- `format_debate_as_markdown(debate)` → Markdown
- `format_debates_list(debates)` → List display

**Helper Functions:**
- `estimate_tokens(text)` → Token count

---

## Data Flow Examples

### Example 1: Run a Debate via CLI

```
$ python -m src.cli debate --topic "AI rights?" --description "..."

┌─────────────────────────────────────────────────────┐
│ CLI: Parse arguments                                 │
│ ✓ topic="AI rights?"                                │
│ ✓ description="..."                                 │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ Orchestrator: run_debate()                          │
│ 1. Create DebateTopic                               │
│ 2. Create 3 AgentConfigs (FOR, AGAINST, SYNTHESIS)  │
│ 3. Call _validate_agents_config()                   │
│ 4. Call _sort_agents_by_role()                      │
└────────────────┬────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼────────┐  ┌──────▼──────────┐
│ Agent 1 (FOR)  │  │ Agent 2 (AGAINST)
│                │  │
│ Prompt:        │  │ Prompt:
│ "Argue FOR"    │  │ "Argue AGAINST
│                │  │  FOR said: [...]"
│ CLI Call:      │  │
│ claude --print │  │ CLI Call:
│ "Argue FOR"    │  │ claude --print "..."
│                │  │
│ Response:      │  │ Response:
│ "AI should..." │  │ "But..."
└────────────────┘  └──────────────────┘
     │                      │
     └────────┬─────────────┘
              │
┌─────────────▼──────────────────┐
│ Agent 3 (SYNTHESIS)             │
│                                 │
│ Prompt:                         │
│ "Synthesize:                    │
│  FOR: AI should...              │
│  AGAINST: But..."               │
│                                 │
│ CLI Call:                       │
│ claude --print "Synthesize..."  │
│                                 │
│ Response:                       │
│ "Both perspectives are valid.." │
└─────────────┬────────────────────┘
              │
┌─────────────▼────────────────────┐
│ Storage: save_debate()            │
│ Write to data/debates/{id}.json   │
│ Update _index.json                │
└─────────────┬────────────────────┘
              │
┌─────────────▼────────────────────┐
│ Format: format_debate_for_display()
│ Display to user                  │
└──────────────────────────────────┘
```

---

### Example 2: Export a Debate

```
$ python -m src.cli debates export {debate_id} --output debate.md --format markdown

┌──────────────────────────┐
│ CLI: Parse arguments     │
│ ✓ debate_id              │
│ ✓ output=debate.md       │
│ ✓ format=markdown        │
└────────────┬─────────────┘
             │
┌────────────▼──────────────┐
│ Orchestrator: get_debate()│
└────────────┬──────────────┘
             │
┌────────────▼──────────────────────┐
│ Storage: get_debate(debate_id)     │
│ Read from data/debates/{id}.json   │
│ Return DebateRecord                │
└────────────┬──────────────────────┘
             │
┌────────────▼──────────────────────────────┐
│ Utils: format_debate_as_markdown()        │
│ Convert DebateRecord to Markdown string   │
└────────────┬──────────────────────────────┘
             │
┌────────────▼──────────────────────────────┐
│ CLI: Write to file                        │
│ Open debate.md                            │
│ Write formatted content                   │
│ Close and confirm                         │
└──────────────────────────────────────────┘
```

---

## Design Principles

### 1. **Separation of Concerns**
- CLI layer handles UI only
- Orchestrator handles logic
- Agents handle subprocess execution
- Storage handles persistence
- Models handle validation

### 2. **Async/Await for Concurrency**
- Agents use `asyncio` for non-blocking I/O
- Future: Enable parallel agent execution
- Timeout protection on all CLI calls

### 3. **Error Handling at Boundaries**
- Validate at input (CLI, models)
- Handle at execution (agents, storage)
- Return graceful responses (AgentResponse)

### 4. **Context-Passing for Quality**
- FOR agent: Plain topic
- AGAINST agent: Topic + FOR response
- SYNTHESIS: Topic + both responses
- Enables coherent debate flow

### 5. **Type Safety with Pydantic**
- All data validated before use
- Clear error messages
- IDE autocomplete support
- JSON serialization built-in

### 6. **Testing at All Layers**
- Unit tests for models (14 tests)
- Integration tests for agents (12 tests)
- Orchestration tests (10 tests)
- CLI tests (17 tests)
- Total: 53 tests, all passing

---

## Extension Points (v2)

### Multi-Turn Debates
```python
session = Session(topic)
round1 = await orchestrator.run_debate_round(topic, agents)
# Users ask follow-up questions
round2 = await orchestrator.run_debate_round(
    topic_refinement="Focus on...",
    previous_context=[round1]
)
```

### Database Backend
```python
class SQLiteStorageBackend(StorageBackend):
    # Implement with SQLite instead of JSON
    # Support complex queries and indexing
```

### Rich Terminal Output
```python
from rich.console import Console
console.print(RichDebateTable(debate))
```

### Batch Processing
```python
debates_config = load_json("debates.json")
for config in debates_config:
    debate = await orchestrator.run_debate(...)
```

---

## Performance Characteristics

**Typical execution times:**
- Single debate: 5-10 seconds (3 Claude Haiku agents)
- Storage (save): <100ms
- Storage (retrieve): <10ms
- JSON serialization: <50ms

**Scaling considerations:**
- Current: In-memory agent queue (sequential)
- Future: Async parallel execution for agents
- Current: JSON files (local)
- Future: Database backend for distributed storage

---

## Summary

The architecture is **modular, testable, and extensible**:
- ✅ Each layer has single responsibility
- ✅ Clear data flow from input to output
- ✅ Comprehensive error handling
- ✅ Type-safe with Pydantic
- ✅ Fully tested (53 tests)
- ✅ Ready for extensions
