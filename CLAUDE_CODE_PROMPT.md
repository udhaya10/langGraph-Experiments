# Multi-Agent Debate System: Complete Build Specification

## 🔍 ENVIRONMENT PREREQUISITES

**STOP - Read this first before any coding!**

### Required CLI Tools (Must be installed and working)

```bash
# Test Claude CLI
claude --model claude-haiku-4-5-20251001 --print "test"
# Expected: Should print "test" and exit successfully

# Test Gemini CLI
gemini --yolo -m gemini-2.5-flash-lite "test"
# Expected: Should print "test" and exit successfully
```

**If either command fails:**
- Claude CLI: https://github.com/anthropics/claude-code
- Gemini CLI: https://github.com/google-gemini/gemini-cli
- Install both before proceeding with ANY SI

### Python Environment
- **Python Version:** 3.11 or higher (will be tested before SI-1)
- **Package Manager:** venv + requirements.txt (standard approach)
- **IDE:** PyCharm Professional

---

## EXECUTIVE SUMMARY

Build a **working multi-agent debate system** that:
1. Orchestrates 3 sequential AI agents (FOR, AGAINST, SYNTHESIS) with context-passing
2. Manages Claude CLI and Gemini CLI integrations via subprocess
3. Handles agent execution with proper error handling and timeouts
4. Stores debate records as JSON with formatted output
5. Provides CLI interface for running and viewing debates
6. Is fully tested against REAL CLIs (not mocked)
7. Is ready to ship and extend

**What we're NOT building (v1):**
- Python API (CLI only)
- Multi-turn debates/session persistence (v2 feature)
- Batch processing (v2 feature)
- Database backend (JSON only)
- Advanced templating (v2 feature)
- Web UI or Rich output (plain text only)

**Tech Stack:** Python 3.11+, Pydantic, Click (CLI)

---

## PROJECT STRUCTURE

```
debate-system/
├── src/
│   ├── __init__.py
│   ├── models.py                      # Data models (Pydantic)
│   ├── agents.py                      # Agent implementations
│   ├── orchestrator.py                # Main debate orchestrator
│   ├── storage.py                     # JSON storage backend
│   ├── cli.py                         # CLI interface (Click)
│   ├── utils.py                       # Helper functions
│   └── exceptions.py                  # Custom exceptions
│
├── tests/
│   ├── __init__.py
│   ├── test_models.py                 # Model unit tests
│   ├── test_agents.py                 # Agent integration tests (real CLI)
│   ├── test_orchestrator.py           # Orchestrator tests
│   └── test_integration.py            # End-to-end tests
│
├── examples/
│   └── basic_debate.py                # Simple example
│
├── data/
│   ├── debates/                       # Stored debate records (JSON)
│   └── logs/                          # Debug logs
│
├── requirements.txt                   # Dependencies
├── setup.py                           # Package configuration
├── .gitignore                         # Git ignore rules
├── README.md                          # Documentation
└── ARCHITECTURE.md                    # System design details
```

---

## SHIPPABLE INCREMENTS (SIs) & TIMELINE

### SI-1: Project Setup + Core Models (1.5 hours)
- Create venv and install dependencies
- Implement 4 Pydantic data models
- Unit tests for models
- **Deliverable:** Can create and validate debate objects

### SI-2: Agent Implementations (2 hours)
- ClaudeAgent class with real CLI subprocess calls
- GeminiAgent class with real CLI subprocess calls
- Response parsing and error handling
- Integration tests with REAL CLIs
- **Deliverable:** Can execute both agent types and get responses

### SI-3: Orchestrator + Context-Passing (1.5 hours)
- DebateOrchestrator class
- Sequential execution with context-passing (FOR → AGAINST → SYNTHESIS)
- Integration tests
- **Deliverable:** Can run a complete debate with agents referencing each other

### SI-4: Storage + CLI (2 hours)
- JSONStorageBackend implementation
- Click CLI commands (debate, list, view, export)
- Integration tests
- **Deliverable:** Full working CLI tool

### SI-5: Examples + Documentation (1 hour)
- Example script showing usage
- README with setup instructions
- Final integration test
- **Deliverable:** Production-ready, shippable system

**Total: ~8 hours spread across 5 increments**

---

## SI-1: DETAILED SPECIFICATION - Core Data Models

### Models to Implement (src/models.py)

**Model 1: AgentConfig**
```python
class AgentConfig:
    - name: str (e.g., "Agent 1")
    - role: str (Literal["FOR", "AGAINST", "SYNTHESIS"])
    - model_provider: str (Literal["claude", "gemini"])
    - model_name: str (e.g., "haiku", "sonnet", "opus", "flash", "pro")
    - model_id: str (Full model ID - auto-generated from provider + name)
    - temperature: float (default: 0.7, range: 0.0-1.0)
    - max_tokens: int (default: 2000)
    - timeout_seconds: int (default: 60)
```

**Model 2: DebateTopic**
```python
class DebateTopic:
    - title: str (e.g., "Should AI have legal rights?")
    - description: str (detailed description of topic)
```

**Model 3: AgentResponse**
```python
class AgentResponse:
    - agent_name: str
    - role: str (Literal["FOR", "AGAINST", "SYNTHESIS"])
    - model_provider: str
    - model_name: str
    - response_text: str (the actual response)
    - execution_time_ms: float
    - success: bool
    - error_message: Optional[str]
```

**Model 4: DebateRecord**
```python
class DebateRecord:
    - debate_id: str (UUID)
    - topic: DebateTopic
    - agents_config: List[AgentConfig]
    - agent_responses: List[AgentResponse]
    - total_execution_time_ms: float
    - created_at: datetime
```

### SI-1 Tests (tests/test_models.py)
- Test AgentConfig creation and validation
- Test DebateTopic creation
- Test AgentResponse creation
- Test DebateRecord creation with responses
- Test invalid inputs (should raise validation errors)

---

## SI-2: DETAILED SPECIFICATION - Agent Implementations

### Architecture: Subprocess-Based CLI Integration

**Key Pattern:**
```python
# Claude execution
subprocess.run([
    "claude",
    "--model", "claude-haiku-4-5-20251001",
    "--print", "prompt_text"
], capture_output=True, text=True, timeout=60)

# Gemini execution
subprocess.run([
    "gemini",
    "--yolo",
    "-m", "gemini-2.5-flash-lite",
    "prompt_text"
], capture_output=True, text=True, timeout=60)
```

### Classes to Implement (src/agents.py)

**Base Agent Class**
```python
class Agent (ABC):
    - config: AgentConfig
    - async execute(prompt: str) -> AgentResponse
    - _build_command(prompt: str) -> List[str]
    - _parse_response(stdout: str, stderr: str, exec_time_ms: float) -> AgentResponse
```

**ClaudeAgent Class**
```python
class ClaudeAgent(Agent):
    - Override _build_command() to build claude command
    - Override _parse_response() to parse claude output
    - Verified working model IDs:
      - claude-haiku-4-5-20251001 (fast, cheap)
      - claude-sonnet-4-5-20250929 (balanced)
      - claude-opus-4-5-20251101 (best quality)
```

**GeminiAgent Class**
```python
class GeminiAgent(Agent):
    - Override _build_command() to build gemini command
    - Override _parse_response() to parse gemini output (remove "Loaded cached credentials" lines)
    - Verified working model IDs:
      - gemini-2.5-flash-lite (cheap)
      - gemini-2.5-flash (balanced)
      - gemini-2.5-pro (best quality)
```

**Agent Factory**
```python
def create_agent(config: AgentConfig) -> Agent:
    - Validates config
    - Returns ClaudeAgent or GeminiAgent based on provider
    - Maps model_name to full model_id
```

### SI-2 Tests (tests/test_agents.py)
- Test ClaudeAgent with real Claude CLI
- Test GeminiAgent with real Gemini CLI
- Test response parsing
- Test timeout handling
- Test error handling (CLI not found, timeout, etc.)

**Critical:** These tests MUST use real CLIs, not mocks!

---

## SI-3: DETAILED SPECIFICATION - Orchestrator with Context-Passing

### Architecture: Sequential Execution with Context

**Execution Flow:**
```
User provides topic
    ↓
Execute FOR agent with topic
    ↓ (Agent 1 response now available)
Execute AGAINST agent with topic + FOR response reference
    ↓ (Agents 1-2 responses available)
Execute SYNTHESIS agent with topic + both responses
    ↓
Return complete DebateRecord
```

### Class to Implement (src/orchestrator.py)

**DebateOrchestrator Class**
```python
class DebateOrchestrator:
    - async run_debate(
        topic: DebateTopic,
        agents_config: List[AgentConfig]
      ) -> DebateRecord:

        1. Validate topic and agents_config
        2. Create agent instances from config
        3. Build FOR prompt from topic
        4. Execute FOR agent, get response
        5. Build AGAINST prompt from topic + FOR response
        6. Execute AGAINST agent, get response
        7. Build SYNTHESIS prompt from topic + both responses
        8. Execute SYNTHESIS agent, get response
        9. Collect all responses into DebateRecord
        10. Store debate (via StorageBackend)
        11. Return DebateRecord

    - get_debate(debate_id: str) -> DebateRecord
    - list_debates(limit: int = 10) -> List[DebateRecord]
```

### Prompt Building (src/utils.py)

```python
def build_for_prompt(topic: DebateTopic) -> str:
    """Build prompt for FOR agent"""
    return f"""
You are arguing in favor of the following topic:

Topic: {topic.title}
Description: {topic.description}

Provide a clear, compelling argument in favor of this topic.
Be specific and evidence-based.
"""

def build_against_prompt(topic: DebateTopic, for_response: str) -> str:
    """Build prompt for AGAINST agent, referencing FOR response"""
    return f"""
You are arguing against the following topic:

Topic: {topic.title}
Description: {topic.description}

The argument in favor of this topic was:
---
{for_response}
---

Provide a clear, compelling counter-argument against this topic.
Address the points made in the FOR argument.
Be specific and evidence-based.
"""

def build_synthesis_prompt(topic: DebateTopic, for_response: str, against_response: str) -> str:
    """Build prompt for SYNTHESIS agent"""
    return f"""
You are synthesizing a debate on the following topic:

Topic: {topic.title}
Description: {topic.description}

ARGUMENT IN FAVOR:
---
{for_response}
---

ARGUMENT AGAINST:
---
{against_response}
---

Provide a balanced synthesis that:
1. Acknowledges the strengths of both arguments
2. Identifies the weaknesses in both arguments
3. Synthesizes a nuanced perspective that considers both viewpoints
4. Offers insights on how to resolve the tensions between the two positions
"""
```

### SI-3 Tests (tests/test_orchestrator.py)
- Test run_debate with real agents
- Test context-passing (AGAINST references FOR, SYNTHESIS references both)
- Test DebateRecord creation
- Test debate storage and retrieval

---

## SI-4: DETAILED SPECIFICATION - Storage & CLI

### Storage Backend (src/storage.py)

**StorageBackend Abstract Class**
```python
class StorageBackend (ABC):
    - save_debate(debate: DebateRecord) -> str  # returns debate_id
    - get_debate(debate_id: str) -> DebateRecord
    - list_debates(limit: int = 10) -> List[DebateRecord]
    - delete_debate(debate_id: str) -> bool
```

**JSONStorageBackend Implementation**
```python
class JSONStorageBackend(StorageBackend):
    - Stores debates in data/debates/{debate_id}.json
    - Maintains data/debates/_index.json for quick lookups
    - File format: debate_id.json contains serialized DebateRecord
    - Index format: list of {id, created_at, topic_title}
```

### CLI Interface (src/cli.py)

Using Click framework, implement:

**Command 1: Run debate**
```bash
debate --topic "Should AI have legal rights?" --description "Discuss the philosophical and legal implications..."
```

**Command 2: List debates**
```bash
debates list --limit 10
```

**Command 3: View debate**
```bash
debates view <debate_id>
```

**Command 4: Export debate**
```bash
debates export <debate_id> --output result.md --format markdown
```

### Output Formatting (plain text)

When displaying a debate, format as:

```
═══════════════════════════════════════════════════════════════
  DEBATE: {topic_title}
═══════════════════════════════════════════════════════════════

TOPIC DESCRIPTION:
{topic_description}

───────────────────────────────────────────────────────────────
1. FOR ARGUMENT
Agent: {agent_name}
Model: {model_name}
Execution Time: {time}ms

{response_text}

───────────────────────────────────────────────────────────────
2. AGAINST ARGUMENT
Agent: {agent_name}
Model: {model_name}
Execution Time: {time}ms

{response_text}

───────────────────────────────────────────────────────────────
3. SYNTHESIS
Agent: {agent_name}
Model: {model_name}
Execution Time: {time}ms

{response_text}

───────────────────────────────────────────────────────────────
SUMMARY
Total Execution Time: {total_time}ms
Created: {created_at}
Debate ID: {debate_id}
═══════════════════════════════════════════════════════════════
```

### SI-4 Tests (tests/test_integration.py)
- Test debate creation → storage → retrieval
- Test CLI commands
- Test export functionality

---

## SI-5: DETAILED SPECIFICATION - Examples & Documentation

### Example Script (examples/basic_debate.py)

```python
"""Simple example of running a debate"""
import asyncio
from src.models import DebateTopic, AgentConfig
from src.orchestrator import DebateOrchestrator

async def main():
    # Create topic
    topic = DebateTopic(
        title="Should AI have legal rights?",
        description="Discuss whether AI systems should be granted legal personhood..."
    )

    # Define agents
    agents_config = [
        AgentConfig(
            name="Claude FOR",
            role="FOR",
            model_provider="claude",
            model_name="sonnet"
        ),
        AgentConfig(
            name="Gemini AGAINST",
            role="AGAINST",
            model_provider="gemini",
            model_name="flash"
        ),
        AgentConfig(
            name="Claude SYNTHESIS",
            role="SYNTHESIS",
            model_provider="claude",
            model_name="opus"
        ),
    ]

    # Run debate
    orchestrator = DebateOrchestrator()
    debate = await orchestrator.run_debate(topic, agents_config)

    # Display results
    print(debate.formatted_output())

if __name__ == "__main__":
    asyncio.run(main())
```

### Documentation Files

**README.md**
- Quick start instructions
- Installation (venv + requirements.txt)
- PyCharm setup steps
- Example usage
- CLI commands reference

**ARCHITECTURE.md**
- System design overview
- How context-passing works
- Subprocess execution details
- Data flow diagram

---

## DEPENDENCIES (requirements.txt)

```
pydantic>=2.0
click>=8.0
python-dotenv>=0.19.0
pytest>=7.0
pytest-asyncio>=0.21.0
```

---

## TESTING STRATEGY

**All tests use REAL CLIs (not mocked)**

### SI-1 Tests
- Unit tests for model validation

### SI-2 Tests
- Integration tests with real Claude and Gemini CLIs
- Tests verify: command building, parsing, error handling

### SI-3 Tests
- Integration tests with real agents
- Tests verify: context-passing, orchestration flow

### SI-4 Tests
- End-to-end tests: run debate → store → retrieve
- CLI command tests

### SI-5 Tests
- Run example script
- Verify all features work

**Test Execution:**
```bash
pytest tests/ -v  # Verbose output
pytest tests/ --tb=short  # Short traceback
```

---

## SUCCESS CRITERIA

✅ All SIs completed and tested
✅ 3 agents execute successfully with REAL CLIs
✅ Context-passing works (agents reference each other)
✅ Debates stored as JSON
✅ All CLI commands work
✅ Example script runs successfully
✅ Code is production-ready
✅ Documentation is complete

---

## NEXT STEPS

1. **Verify environment:** Test both CLIs work before starting SI-1
2. **SI-1:** Create project structure and models
3. **SI-2:** Implement agents with real CLI integration
4. **SI-3:** Build orchestrator with context-passing
5. **SI-4:** Add storage and CLI commands
6. **SI-5:** Polish and document
7. **Ship:** Ready for GitHub

---

**This is your complete specification. Each SI should take ~2 hours including testing. Start with SI-1!** 🚀
