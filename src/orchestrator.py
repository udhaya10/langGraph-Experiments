"""
DebateOrchestrator - Main orchestration logic
Manages sequential execution with context-passing
"""
import time
from typing import List
from src.models import DebateTopic, AgentConfig, DebateRecord
from src.agents import create_agent
from src.storage import JSONStorageBackend


# Prompt building functions
def build_for_prompt(topic: DebateTopic) -> str:
    """Build prompt for FOR agent"""
    return f"""You are arguing in favor of the following topic:

Topic: {topic.title}
Description: {topic.description}

Provide a clear, compelling argument in favor of this topic.
Be specific and evidence-based.
Keep your response focused and substantive."""


def build_against_prompt(topic: DebateTopic, for_response: str) -> str:
    """Build prompt for AGAINST agent, referencing FOR response"""
    return f"""You are arguing against the following topic:

Topic: {topic.title}
Description: {topic.description}

The argument in favor of this topic was:
---
{for_response}
---

Provide a clear, compelling counter-argument against this topic.
Address the points made in the FOR argument.
Be specific and evidence-based.
Keep your response focused and substantive."""


def build_synthesis_prompt(topic: DebateTopic, for_response: str, against_response: str) -> str:
    """Build prompt for SYNTHESIS agent"""
    return f"""You are synthesizing a debate on the following topic:

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

Keep your synthesis thoughtful and balanced."""


class DebateOrchestrator:
    """Orchestrates multi-agent debates with context-passing"""

    def __init__(self, storage_backend=None):
        """Initialize orchestrator with optional storage backend"""
        self.storage = storage_backend or JSONStorageBackend()

    def _validate_agents_config(self, agents_config: List[AgentConfig]) -> None:
        """Validate that agents have correct roles"""
        if len(agents_config) != 3:
            raise ValueError(
                f"Debate requires exactly 3 agents, got {len(agents_config)}"
            )

        roles = [agent.role for agent in agents_config]
        expected_roles = {"FOR", "AGAINST", "SYNTHESIS"}

        if set(roles) != expected_roles:
            raise ValueError(
                f"Agents must have roles FOR, AGAINST, SYNTHESIS. Got: {roles}"
            )

        # Check no duplicate roles
        if len(roles) != len(set(roles)):
            raise ValueError("Duplicate agent roles found")

    def _sort_agents_by_role(self, agents_config: List[AgentConfig]) -> List[AgentConfig]:
        """Sort agents in execution order: FOR, AGAINST, SYNTHESIS"""
        role_order = {"FOR": 0, "AGAINST": 1, "SYNTHESIS": 2}
        return sorted(agents_config, key=lambda a: role_order[a.role])

    async def run_debate(
        self,
        topic: DebateTopic,
        agents_config: List[AgentConfig]
    ) -> DebateRecord:
        """
        Run a complete debate with context-passing

        Execution flow:
        1. FOR agent gets topic
        2. AGAINST agent gets topic + FOR response
        3. SYNTHESIS agent gets topic + both responses

        Returns: DebateRecord with all responses
        """
        # Validate configuration
        self._validate_agents_config(agents_config)

        # Sort agents by execution order
        sorted_agents = self._sort_agents_by_role(agents_config)

        # Track start time
        start_time = time.time()

        # Create agent instances
        agents = [create_agent(config) for config in sorted_agents]

        # Execute agents sequentially with context-passing
        responses = []

        # Step 1: Execute FOR agent
        for_agent = agents[0]
        for_prompt = build_for_prompt(topic)
        for_response = await for_agent.execute(for_prompt)
        responses.append(for_response)

        # Step 2: Execute AGAINST agent (with FOR response context)
        against_agent = agents[1]
        against_prompt = build_against_prompt(topic, for_response.response_text)
        against_response = await against_agent.execute(against_prompt)
        responses.append(against_response)

        # Step 3: Execute SYNTHESIS agent (with both responses context)
        synthesis_agent = agents[2]
        synthesis_prompt = build_synthesis_prompt(
            topic,
            for_response.response_text,
            against_response.response_text
        )
        synthesis_response = await synthesis_agent.execute(synthesis_prompt)
        responses.append(synthesis_response)

        # Calculate total time
        total_execution_time = (time.time() - start_time) * 1000

        # Create debate record
        debate = DebateRecord(
            topic=topic,
            agents_config=agents_config,
            agent_responses=responses,
            total_execution_time_ms=total_execution_time
        )

        # Store debate
        self.storage.save_debate(debate)

        return debate

    def get_debate(self, debate_id: str) -> DebateRecord:
        """Retrieve a stored debate by ID"""
        return self.storage.get_debate(debate_id)

    def list_debates(self, limit: int = 10) -> list:
        """List stored debates"""
        return self.storage.list_debates(limit=limit)
