"""
Utility functions for formatting and helpers
"""
from src.models import DebateRecord


def format_debate_for_display(debate: DebateRecord) -> str:
    """Format a debate record for terminal display"""
    lines = []

    # Header
    lines.append("=" * 70)
    lines.append(f"  DEBATE: {debate.topic.title}")
    lines.append("=" * 70)
    lines.append("")

    # Topic
    lines.append("TOPIC DESCRIPTION:")
    lines.append(debate.topic.description)
    lines.append("")

    # Responses
    for i, response in enumerate(debate.agent_responses, 1):
        lines.append("-" * 70)
        lines.append(f"{i}. {response.role} ARGUMENT")
        lines.append(f"Agent: {response.agent_name}")
        lines.append(f"Model: {response.model_name}")
        lines.append(f"Execution Time: {response.execution_time_ms:.1f}ms")
        lines.append("")
        lines.append(response.response_text)
        lines.append("")

    # Summary
    lines.append("-" * 70)
    lines.append("SUMMARY")
    lines.append(f"Total Execution Time: {debate.total_execution_time_ms:.1f}ms")
    lines.append(f"Created: {debate.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Debate ID: {debate.debate_id}")
    lines.append("=" * 70)

    return "\n".join(lines)


def format_debate_as_markdown(debate: DebateRecord) -> str:
    """Format a debate record as Markdown"""
    lines = []

    # Title
    lines.append(f"# {debate.topic.title}")
    lines.append("")

    # Topic
    lines.append("## Topic Description")
    lines.append("")
    lines.append(debate.topic.description)
    lines.append("")

    # Responses
    for i, response in enumerate(debate.agent_responses, 1):
        role_name = {
            "FOR": "Affirmative Argument",
            "AGAINST": "Negative Argument",
            "SYNTHESIS": "Synthesis"
        }.get(response.role, response.role)

        lines.append(f"## {i}. {role_name}")
        lines.append("")
        lines.append(f"**Agent:** {response.agent_name}")
        lines.append("")
        lines.append(f"**Model:** {response.model_name}")
        lines.append("")
        lines.append(f"**Execution Time:** {response.execution_time_ms:.1f}ms")
        lines.append("")
        lines.append(response.response_text)
        lines.append("")

    # Metadata
    lines.append("---")
    lines.append("## Metadata")
    lines.append("")
    lines.append(f"- **Total Execution Time:** {debate.total_execution_time_ms:.1f}ms")
    lines.append(f"- **Debate ID:** `{debate.debate_id}`")
    lines.append(f"- **Created:** {debate.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    return "\n".join(lines)


def format_debates_list(debates: list) -> str:
    """Format list of debates for display"""
    if not debates:
        return "No debates found."

    lines = ["Stored Debates:"]
    lines.append("")

    for i, debate in enumerate(debates, 1):
        lines.append(f"{i}. {debate.topic.title}")
        lines.append(f"   ID: {debate.debate_id}")
        lines.append(f"   Created: {debate.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"   Agents: {len(debate.agent_responses)}")
        lines.append("")

    return "\n".join(lines)


def estimate_tokens(text: str) -> int:
    """Rough token estimation (approximately 4 chars per token)"""
    return len(text) // 4
