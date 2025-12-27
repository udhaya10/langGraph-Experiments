
import plotly.graph_objects as go
import json

# Data
data = {
  "documents": [
    {
      "rank": "1 ⭐",
      "name": "CLAUDE_CODE_PROMPT.md",
      "lines": "1093",
      "purpose": "Main Specification",
      "when_to_use": "Give to Claude Code immediately",
      "key_topics": "Architecture, Models, Implementation, Timeline"
    },
    {
      "rank": "2",
      "name": "IMPLEMENTATION_REFERENCE.md",
      "lines": "895",
      "purpose": "Code Examples & Patterns",
      "when_to_use": "Reference during implementation",
      "key_topics": "Async Patterns, Agent Code, Storage, CLI, Tests"
    },
    {
      "rank": "3",
      "name": "GITHUB_SETUP_GUIDE.md",
      "lines": "578",
      "purpose": "Deployment & CI/CD",
      "when_to_use": "After code is complete",
      "key_topics": "Repository Setup, Workflows, Commits, Release"
    },
    {
      "rank": "4",
      "name": "FINAL_VERIFIED_COMMANDS.md",
      "lines": "426",
      "purpose": "CLI Syntax Reference",
      "when_to_use": "Quick lookup while building",
      "key_topics": "Working Commands, Model IDs, Copy-Paste Ready"
    },
    {
      "rank": "5",
      "name": "COMPLETE_WORKING_MODELS_VERIFIED.md",
      "lines": "424",
      "purpose": "Model Specifications",
      "when_to_use": "When choosing agents/models",
      "key_topics": "All 6 Models, Quality, Cost, Comparison"
    },
    {
      "rank": "6",
      "name": "PROMPT_INDEX.md",
      "lines": "394",
      "purpose": "Navigation & Organization",
      "when_to_use": "Finding specific information",
      "key_topics": "Document Index, Quick Links, Relationships"
    }
  ]
}

docs = data["documents"]

# Calculate total lines
total_lines = sum(int(doc["lines"]) for doc in docs)

# Prepare table data with exact values from JSON
ranks = [doc["rank"] for doc in docs]
names = [doc["name"] for doc in docs]
lines = [doc["lines"] for doc in docs]
purposes = [doc["purpose"] for doc in docs]
when_to_use = [doc["when_to_use"] for doc in docs]
key_topics = [doc["key_topics"] for doc in docs]

# Create alternating row colors for all columns
fill_colors = []
for i in range(6):  # 6 columns
    colors = []
    for j in range(len(docs)):
        if j % 2 == 0:
            colors.append('#ffffff')
        else:
            colors.append('#f8f8f8')
    fill_colors.append(colors)

# Create table with larger fonts and better spacing
fig = go.Figure(data=[go.Table(
    header=dict(
        values=['<b>Rank</b>', '<b>Document Name</b>', '<b>Lines</b>', '<b>Purpose</b>', '<b>When to Use</b>', '<b>Key Topics</b>'],
        fill_color='#1FB8CD',
        align=['center', 'left', 'right', 'left', 'left', 'left'],
        font=dict(color='white', size=14),
        height=50,
        line=dict(color='white', width=2)
    ),
    cells=dict(
        values=[ranks, names, lines, purposes, when_to_use, key_topics],
        fill_color=fill_colors,
        align=['center', 'left', 'right', 'left', 'left', 'left'],
        font=dict(color='#2d2d2d', size=13),
        height=50,
        line=dict(color='#e0e0e0', width=1)
    ),
    columnwidth=[80, 320, 80, 200, 260, 380]
)])

# Update layout with clearer title
fig.update_layout(
    title={
        "text": f"Claude Code Documentation Reference Overview<br><span style='font-size: 18px; font-weight: normal;'>6 documents totaling {total_lines:,} lines, organized by priority</span>",
        "x": 0.5,
        "xanchor": "center"
    }
)

# Save as PNG and SVG
fig.write_image("claude_docs_table.png")
fig.write_image("claude_docs_table.svg", format="svg")
