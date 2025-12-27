# Multi-Agent Debate System

A production-ready Python system for orchestrating multi-agent debates using Claude and Gemini CLIs.

**Features:**
- 🤖 Orchestrates 3 sequential AI agents (FOR, AGAINST, SYNTHESIS)
- 🔄 Context-passing: each agent sees previous arguments
- 💾 JSON storage of all debates with metadata
- 🖥️ Command-line interface for running and managing debates
- 📝 Multiple export formats (Text, Markdown, JSON)
- ✅ 53 comprehensive tests (all passing)
- 🔌 Real CLI integration (no API keys needed)

---

## Quick Start

### Prerequisites

- Python 3.11+
- Claude CLI installed and working
- Gemini CLI installed and working

### Installation

1. **Verify CLIs are installed:**
   ```bash
   claude --model claude-haiku-4-5-20251001 --print "test"
   gemini --yolo -m gemini-2.5-flash-lite "test"
   ```

2. **Clone and setup project:**
   ```bash
   cd /Users/udhaya10/workspace/langGraphExperiments
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run tests to verify everything works:**
   ```bash
   pytest tests/ -v
   ```

---

## Usage

### Via Command Line

#### Run a Debate
```bash
source venv/bin/activate
python -m src.cli debate \
  --topic "Should AI have legal rights?" \
  --description "Discuss whether AI systems should be granted legal personhood and rights"
```

Output will show:
- Affirmative argument (FOR)
- Negative argument (AGAINST) - referencing FOR
- Synthesis - integrating both perspectives
- Debate ID for future reference

#### List Stored Debates
```bash
python -m src.cli debates list --limit 10
```

#### View a Specific Debate
```bash
python -m src.cli debates view 550e8400-e29b-41d4-a716-446655440000
```

#### Export a Debate
```bash
# As Markdown
python -m src.cli debates export 550e8400-e29b-41d4-a716-446655440000 \
  --output debate.md --format markdown

# As JSON
python -m src.cli debates export 550e8400-e29b-41d4-a716-446655440000 \
  --output debate.json --format json

# As Text
python -m src.cli debates export 550e8400-e29b-41d4-a716-446655440000 \
  --output debate.txt --format text
```

### Via Python API

```python
import asyncio
from src.models import DebateTopic, AgentConfig
from src.orchestrator import DebateOrchestrator
from src.utils import format_debate_for_display

async def run_debate():
    # Create topic
    topic = DebateTopic(
        title="Is Python good?",
        description="Discuss pros and cons of Python"
    )

    # Define agents
    agents_config = [
        AgentConfig(
            name="Claude FOR",
            role="FOR",
            model_provider="claude",
            model_name="haiku"
        ),
        AgentConfig(
            name="Claude AGAINST",
            role="AGAINST",
            model_provider="claude",
            model_name="haiku"
        ),
        AgentConfig(
            name="Claude SYNTHESIS",
            role="SYNTHESIS",
            model_provider="claude",
            model_name="haiku"
        ),
    ]

    # Run debate
    orchestrator = DebateOrchestrator()
    debate = await orchestrator.run_debate(topic, agents_config)

    # Display results
    print(format_debate_for_display(debate))

    # Access individual responses
    for response in debate.agent_responses:
        print(f"{response.role}: {response.response_text}")
        print(f"Execution time: {response.execution_time_ms}ms")

# Run it
asyncio.run(run_debate())
```

---

## PyCharm Setup

1. **Open Project:**
   - File → Open → Select `/Users/udhaya10/workspace/langGraphExperiments`

2. **Configure Python Interpreter:**
   - Preferences → Project → Python Interpreter
   - Click ⚙️ → Add → Existing Environment
   - Select: `/Users/udhaya10/workspace/langGraphExperiments/venv/bin/python`

3. **Run Tests in PyCharm:**
   - Right-click `tests/test_models.py` → Run pytest
   - Or: View → Run Tool Window → Run all tests

4. **Run CLI Commands:**
   - Terminal in PyCharm
   - `source venv/bin/activate`
   - `python -m src.cli debate --topic "..." --description "..."`

---

## Project Structure

```
debate-system/
├── src/
│   ├── __init__.py
│   ├── models.py              # Pydantic models (AgentConfig, DebateTopic, etc.)
│   ├── agents.py              # Claude & Gemini agent implementations
│   ├── orchestrator.py        # Main orchestration logic
│   ├── storage.py             # JSON storage backend
│   ├── cli.py                 # Click CLI commands
│   ├── utils.py               # Formatting & utility functions
│   └── exceptions.py          # Custom exceptions
│
├── tests/
│   ├── test_models.py         # Model validation tests (14 tests)
│   ├── test_agents.py         # Agent execution tests (12 tests)
│   ├── test_orchestrator.py   # Orchestrator logic tests (10 tests)
│   └── test_cli.py            # CLI command tests (17 tests)
│
├── examples/
│   └── basic_debate.py        # Simple usage example
│
├── data/
│   ├── debates/               # Stored debate JSON files
│   └── logs/                  # Debug logs (optional)
│
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── .gitignore                 # Git ignore rules
```

---

## Architecture

### Sequential Execution with Context-Passing

The system executes agents sequentially, with each agent seeing the results of previous agents:

```
Step 1: FOR Agent
  Prompt: "Topic: Should AI have rights?"
  Response: "AI systems demonstrate sentience..."

Step 2: AGAINST Agent
  Prompt: "Topic: Should AI have rights?
           The FOR argument was: 'AI systems demonstrate sentience...'
           Counter this argument..."
  Response: "However, sentience is not clearly defined..."

Step 3: SYNTHESIS Agent
  Prompt: "Topic: Should AI have rights?
           FOR: 'AI systems demonstrate sentience...'
           AGAINST: 'However, sentience is not clearly defined...'
           Synthesize both perspectives..."
  Response: "Both arguments present valid points..."
```

### Data Storage

Debates are stored as JSON files:
```
data/debates/
├── 550e8400-e29b-41d4-a716-446655440000.json
├── f47ac10b-58cc-4372-a567-0e02b2c3d479.json
└── _index.json  (fast lookup index)
```

Each debate file contains:
- Debate metadata (ID, creation time)
- Topic title and description
- Agent configurations
- All 3 agent responses with execution times
- Total execution time

---

## Testing

### Run All Tests
```bash
source venv/bin/activate
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_models.py -v
pytest tests/test_agents.py -v
pytest tests/test_orchestrator.py -v
pytest tests/test_cli.py -v
```

### Run Specific Test
```bash
pytest tests/test_models.py::TestAgentConfig::test_agent_config_creation_with_claude -v
```

### Test Coverage

```
53 Total Tests - ALL PASSING ✅

SI-1: Models                     14 tests ✅
SI-2: Agents (real CLI)          12 tests ✅
SI-3: Orchestrator               10 tests ✅
SI-4: CLI + Storage              17 tests ✅
─────────────────────────────────────────
TOTAL                            53 tests ✅
```

**Key Testing Features:**
- Real Claude and Gemini CLI integration (not mocked)
- Async/await testing with pytest-asyncio
- CLI command testing with Click's CliRunner
- Comprehensive error handling tests
- Context-passing verification

---

## Configuration

### Agent Models

**Claude Models (fast execution):**
- `haiku` → `claude-haiku-4-5-20251001` (fastest, cheapest)
- `sonnet` → `claude-sonnet-4-5-20250929` (balanced)
- `opus` → `claude-opus-4-5-20251101` (best quality)

**Gemini Models (alternative):**
- `flash-lite` → `gemini-2.5-flash-lite` (fastest, cheapest)
- `flash` → `gemini-2.5-flash` (balanced)
- `pro` → `gemini-2.5-pro` (best quality)

### Default Configuration

```python
temperature: 0.7      # Creativity level (0.0-1.0)
max_tokens: 2000      # Max response length
timeout_seconds: 60   # CLI execution timeout
```

---

## Troubleshooting

### Claude CLI Not Found
```bash
# Verify installation
claude --model claude-haiku-4-5-20251001 --print "test"

# If not installed, follow:
# https://github.com/anthropics/claude-code
```

### Gemini CLI Not Found
```bash
# Verify installation
gemini --yolo -m gemini-2.5-flash-lite "test"

# If not installed, follow:
# https://github.com/google-gemini/gemini-cli
```

### Tests Timing Out
- Increase timeout in agent config: `timeout_seconds=120`
- Check network connectivity to Claude/Gemini services
- Try with faster models (`haiku`, `flash-lite`)

### Storage Issues
- Verify `data/debates/` directory exists
- Check write permissions: `chmod 755 data/`
- Delete `data/debates/_index.json` to rebuild index

---

## Next Steps / Extensions (v2)

- [ ] Multi-turn debates with session management
- [ ] Database backend (SQLite/PostgreSQL)
- [ ] Web UI dashboard
- [ ] Advanced templating system
- [ ] Debate metrics and analytics
- [ ] Batch processing from JSON files
- [ ] Rich terminal output formatting
- [ ] Debate comparison tools

---

## License

MIT License - Feel free to use and modify!

---

## Support

For issues or questions:
1. Check the test files for usage examples
2. Review CLAUDE_CODE_PROMPT.md for technical details
3. Run: `python -m src.cli --help` for CLI options

---

**Ready to use! Start debating!** 🚀
