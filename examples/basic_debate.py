"""
Basic example: How to run a debate programmatically
"""
import asyncio
from src.models import DebateTopic, AgentConfig
from src.orchestrator import DebateOrchestrator
from src.utils import format_debate_for_display


async def main():
    """Run a basic debate example"""

    # Step 1: Define the topic
    topic = DebateTopic(
        title="Should AI have legal rights?",
        description="Discuss whether artificial intelligence systems should be granted "
                    "legal personhood and associated rights in the future."
    )

    # Step 2: Define the agents (FOR, AGAINST, SYNTHESIS)
    agents_config = [
        AgentConfig(
            name="Claude FOR",
            role="FOR",
            model_provider="claude",
            model_name="haiku",
            temperature=0.7,
            max_tokens=2000,
            timeout_seconds=60
        ),
        AgentConfig(
            name="Claude AGAINST",
            role="AGAINST",
            model_provider="claude",
            model_name="haiku",
            temperature=0.7,
            max_tokens=2000,
            timeout_seconds=60
        ),
        AgentConfig(
            name="Claude SYNTHESIS",
            role="SYNTHESIS",
            model_provider="claude",
            model_name="haiku",
            temperature=0.7,
            max_tokens=2000,
            timeout_seconds=60
        ),
    ]

    # Step 3: Create orchestrator and run debate
    print("🚀 Starting debate: " + topic.title)
    print("-" * 70)

    orchestrator = DebateOrchestrator()
    debate = await orchestrator.run_debate(topic, agents_config)

    # Step 4: Display results
    print(format_debate_for_display(debate))

    # Step 5: Show debate metadata
    print("\n📋 Debate Metadata:")
    print(f"   Debate ID: {debate.debate_id}")
    print(f"   Total Time: {debate.total_execution_time_ms:.1f}ms")
    print(f"   Number of Responses: {len(debate.agent_responses)}")
    print(f"   Agents: {', '.join([a.name for a in debate.agents_config])}")

    # Step 6: Show how to retrieve the debate later
    print(f"\n💡 To view this debate again, use:")
    print(f"   python -m src.cli debates view {debate.debate_id}")
    print(f"\n   Or export it:")
    print(f"   python -m src.cli debates export {debate.debate_id} --output debate.md --format markdown")


if __name__ == "__main__":
    asyncio.run(main())
