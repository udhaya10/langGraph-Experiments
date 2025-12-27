# Provider Selection Guide

## Overview

You can now run debates with different AI providers:
- **Claude** (default) - Uses Claude Haiku for all agents
- **Gemini** - Uses Gemini Flash for all agents
- **Mixed** - Uses Claude for FOR and SYNTHESIS, Gemini for AGAINST

---

## Quick Start

### Option 1: Claude (Default)

```bash
source venv/bin/activate

python -m src.cli debate \
  --topic "Should AI have rights?" \
  --description "Discuss whether AI systems deserve legal rights"
```

**Output:**
```
🔄 Starting debate: Should AI have rights?
   Description: Discuss whether AI systems deserve legal rights
   Provider: claude

[Agent 1: Claude FOR - executing...]
[Agent 2: Claude AGAINST - executing...]
[Agent 3: Claude SYNTHESIS - executing...]
```

---

### Option 2: Gemini

```bash
source venv/bin/activate

python -m src.cli debate \
  --topic "Should AI have rights?" \
  --description "Discuss whether AI systems deserve legal rights" \
  --provider gemini
```

**Output:**
```
🔄 Starting debate: Should AI have rights?
   Description: Discuss whether AI systems deserve legal rights
   Provider: gemini

[Agent 1: Gemini FOR - executing...]
[Agent 2: Gemini AGAINST - executing...]
[Agent 3: Gemini SYNTHESIS - executing...]
```

---

### Option 3: Mixed (Claude + Gemini)

```bash
source venv/bin/activate

python -m src.cli debate \
  --topic "Should AI have rights?" \
  --description "Discuss whether AI systems deserve legal rights" \
  --provider mixed
```

**Output:**
```
🔄 Starting debate: Should AI have rights?
   Description: Discuss whether AI systems deserve legal rights
   Provider: mixed

[Agent 1: Claude FOR - executing...]
[Agent 2: Gemini AGAINST - executing...]
[Agent 3: Claude SYNTHESIS - executing...]
```

---

## Provider Configurations

### Claude Provider
- **Agent Role** | **Model** | **Details**
- FOR | Claude Haiku | Argues in favor of topic
- AGAINST | Claude Haiku | Counters the FOR argument
- SYNTHESIS | Claude Haiku | Synthesizes both perspectives

### Gemini Provider
- **Agent Role** | **Model** | **Details**
- FOR | Gemini Flash | Argues in favor of topic
- AGAINST | Gemini Flash | Counters the FOR argument
- SYNTHESIS | Gemini Flash | Synthesizes both perspectives

### Mixed Provider
- **Agent Role** | **Model** | **Details**
- FOR | Claude Haiku | Argues in favor of topic
- AGAINST | Gemini Flash | Counters from different perspective
- SYNTHESIS | Claude Haiku | Unifies both viewpoints

---

## Export Results

After running a debate, you can export the results:

```bash
# Get the debate ID from the output
# Then export as needed:

# Export as Markdown
python -m src.cli debates export {debate_id} \
  --output debate.md \
  --format markdown

# Export as JSON
python -m src.cli debates export {debate_id} \
  --output debate.json \
  --format json

# Export as Text
python -m src.cli debates export {debate_id} \
  --output debate.txt \
  --format text
```

---

## Troubleshooting

### Error: `Provider 'gemini' not recognized`
Make sure you're using the correct spelling: `claude`, `gemini`, or `mixed`

```bash
# ✅ Correct
python -m src.cli debate --topic "..." --provider gemini

# ❌ Wrong
python -m src.cli debate --topic "..." --provider "Gemini"
```

### Error: `gemini: command not found`
Make sure Gemini CLI is installed and in your PATH:

```bash
# Test if Gemini CLI is available
gemini --yolo -m gemini-2.5-flash "Hello"
```

### Error: `claude: command not found`
Make sure Claude CLI is installed and in your PATH:

```bash
# Test if Claude CLI is available
claude --model claude-haiku-4-5-20251001 --print "Hello"
```

---

## Testing Different Providers

### Test 1: Quick Debate with Claude
```bash
source venv/bin/activate

python -m src.cli debate \
  --topic "Is Python good?" \
  --description "Quick test debate"
```

### Test 2: Quick Debate with Gemini
```bash
source venv/bin/activate

python -m src.cli debate \
  --topic "Is Python good?" \
  --description "Quick test debate" \
  --provider gemini
```

### Test 3: Mixed Debate
```bash
source venv/bin/activate

python -m src.cli debate \
  --topic "Is Python good?" \
  --description "Quick test debate" \
  --provider mixed
```

### Test 4: Complex Topic with Gemini
```bash
source venv/bin/activate

python -m src.cli debate \
  --topic "Will AI replace human creativity?" \
  --description "Discuss whether AI can truly be creative or just mimics human patterns" \
  --provider gemini
```

---

## Compare Results

1. **Run with Claude:**
   ```bash
   python -m src.cli debate --topic "Your topic" --description "Your description"
   # Note the debate_id
   ```

2. **Run with Gemini:**
   ```bash
   python -m src.cli debate --topic "Your topic" --description "Your description" --provider gemini
   # Note the debate_id
   ```

3. **View both debates:**
   ```bash
   python -m src.cli debates view {claude_debate_id}
   python -m src.cli debates view {gemini_debate_id}
   ```

4. **Compare the responses** - Notice differences in reasoning style and perspective

---

## Future: Multi-Turn Deliberation (v2)

Currently, each debate runs once per agent. The exciting future enhancement you mentioned:
- Claude gives opinion (FOR)
- Gemini responds (AGAINST)
- They both see each other's arguments
- They deliberate/reconsider
- Share refined opinions
- Continue until consensus

This would create true collaborative reasoning between different AI systems!

---

## Command Reference

```bash
# List all stored debates
python -m src.cli debates list

# View a debate
python -m src.cli debates view {debate_id}

# View as markdown
python -m src.cli debates view {debate_id} --format markdown

# Export debate
python -m src.cli debates export {debate_id} --output file.md --format markdown
```

---

## Notes

- Each agent takes 2-5 seconds to execute (real CLI calls)
- Full debate (3 agents) typically takes 6-15 seconds
- All debates are stored in `data/debates/` directory
- Use debate IDs to track and reference debates
- Mix and match providers based on your needs!

---

**Ready to test? Start with a simple debate and compare Claude vs Gemini responses!**
