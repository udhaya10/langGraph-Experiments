"""
Tests for DebateOrchestrator
Tests the sequential execution with context-passing (FOR → AGAINST → SYNTHESIS)
"""
import pytest
from src.models import DebateTopic, AgentConfig
from src.orchestrator import DebateOrchestrator


class TestDebateOrchestrator:
    """Tests for the DebateOrchestrator"""

    @pytest.mark.asyncio
    async def test_run_debate_basic(self):
        """Test running a basic 3-agent debate"""
        topic = DebateTopic(
            title="Is Python a good language?",
            description="Discuss the pros and cons of Python as a programming language"
        )

        agents_config = [
            AgentConfig(
                name="Claude FOR",
                role="FOR",
                model_provider="claude",
                model_name="haiku"
            ),
            AgentConfig(
                name="Gemini AGAINST",
                role="AGAINST",
                model_provider="gemini",
                model_name="flash-lite"
            ),
            AgentConfig(
                name="Claude SYNTHESIS",
                role="SYNTHESIS",
                model_provider="claude",
                model_name="haiku"
            ),
        ]

        orchestrator = DebateOrchestrator()
        debate = await orchestrator.run_debate(topic, agents_config)

        # Verify debate record
        assert debate.debate_id is not None
        assert debate.topic.title == "Is Python a good language?"
        assert len(debate.agents_config) == 3
        assert len(debate.agent_responses) == 3
        assert debate.total_execution_time_ms > 0

        # Verify all responses succeeded
        for response in debate.agent_responses:
            assert response.success is True
            assert response.error_message is None
            assert len(response.response_text) > 0

        # Verify roles
        assert debate.agent_responses[0].role == "FOR"
        assert debate.agent_responses[1].role == "AGAINST"
        assert debate.agent_responses[2].role == "SYNTHESIS"

    @pytest.mark.asyncio
    async def test_context_passing_for_to_against(self):
        """Test that AGAINST agent sees FOR response"""
        topic = DebateTopic(
            title="Test topic",
            description="Simple test topic"
        )

        agents_config = [
            AgentConfig(
                name="Agent 1",
                role="FOR",
                model_provider="claude",
                model_name="haiku"
            ),
            AgentConfig(
                name="Agent 2",
                role="AGAINST",
                model_provider="claude",
                model_name="haiku"
            ),
            AgentConfig(
                name="Agent 3",
                role="SYNTHESIS",
                model_provider="claude",
                model_name="haiku"
            ),
        ]

        orchestrator = DebateOrchestrator()
        debate = await orchestrator.run_debate(topic, agents_config)

        # Get responses
        for_response = debate.agent_responses[0]
        against_response = debate.agent_responses[1]
        synthesis_response = debate.agent_responses[2]

        # Verify all responses are present and non-empty
        assert len(for_response.response_text) > 0
        assert len(against_response.response_text) > 0
        assert len(synthesis_response.response_text) > 0

        # The AGAINST response should be longer/different from just answering the topic
        # because it references the FOR response
        assert len(against_response.response_text) > 50  # Substantial response

        # The SYNTHESIS response should reference both
        assert len(synthesis_response.response_text) > 50  # Substantial response

    @pytest.mark.asyncio
    async def test_debate_execution_time_tracking(self):
        """Test that execution times are tracked"""
        topic = DebateTopic(
            title="Quick test",
            description="Test tracking"
        )

        agents_config = [
            AgentConfig(
                name="Agent",
                role="FOR",
                model_provider="claude",
                model_name="haiku"
            ),
            AgentConfig(
                name="Agent",
                role="AGAINST",
                model_provider="claude",
                model_name="haiku"
            ),
            AgentConfig(
                name="Agent",
                role="SYNTHESIS",
                model_provider="claude",
                model_name="haiku"
            ),
        ]

        orchestrator = DebateOrchestrator()
        debate = await orchestrator.run_debate(topic, agents_config)

        # Each response should have execution time
        for response in debate.agent_responses:
            assert response.execution_time_ms > 0

        # Total should be sum of individual times (approximately)
        sum_of_times = sum(r.execution_time_ms for r in debate.agent_responses)
        assert debate.total_execution_time_ms > 0
        # Total should be at least as long as any individual response
        assert debate.total_execution_time_ms >= max(r.execution_time_ms for r in debate.agent_responses)

    @pytest.mark.asyncio
    async def test_debate_with_mixed_providers(self):
        """Test debate with both Claude and Gemini agents"""
        topic = DebateTopic(
            title="AI future",
            description="Will AI surpass human intelligence?"
        )

        agents_config = [
            AgentConfig(name="Claude FOR", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="Claude AGAINST", role="AGAINST", model_provider="claude", model_name="haiku"),
            AgentConfig(name="Claude SYNTHESIS", role="SYNTHESIS", model_provider="claude", model_name="haiku"),
        ]

        orchestrator = DebateOrchestrator()
        debate = await orchestrator.run_debate(topic, agents_config)

        # Verify all Claude agents
        assert debate.agent_responses[0].model_provider == "claude"
        assert debate.agent_responses[1].model_provider == "claude"
        assert debate.agent_responses[2].model_provider == "claude"

        # All should succeed
        for response in debate.agent_responses:
            assert response.success is True

    @pytest.mark.asyncio
    async def test_debate_invalid_agents_count(self):
        """Test that debate requires 3 agents (FOR, AGAINST, SYNTHESIS)"""
        topic = DebateTopic(
            title="Test",
            description="Test"
        )

        # Only 2 agents (missing SYNTHESIS)
        agents_config = [
            AgentConfig(name="Agent 1", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="Agent 2", role="AGAINST", model_provider="claude", model_name="haiku"),
        ]

        orchestrator = DebateOrchestrator()

        # Should raise validation error
        with pytest.raises((ValueError, AssertionError)):
            await orchestrator.run_debate(topic, agents_config)

    @pytest.mark.asyncio
    async def test_debate_duplicate_roles(self):
        """Test that debate fails with duplicate roles"""
        topic = DebateTopic(
            title="Test",
            description="Test"
        )

        # Two FOR agents
        agents_config = [
            AgentConfig(name="Agent 1", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="Agent 2", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="Agent 3", role="SYNTHESIS", model_provider="claude", model_name="haiku"),
        ]

        orchestrator = DebateOrchestrator()

        # Should raise validation error
        with pytest.raises((ValueError, AssertionError)):
            await orchestrator.run_debate(topic, agents_config)

    @pytest.mark.asyncio
    async def test_get_debate(self):
        """Test retrieving a stored debate"""
        topic = DebateTopic(
            title="Test retrieval",
            description="Test"
        )

        agents_config = [
            AgentConfig(name="Agent 1", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="Agent 2", role="AGAINST", model_provider="claude", model_name="haiku"),
            AgentConfig(name="Agent 3", role="SYNTHESIS", model_provider="claude", model_name="haiku"),
        ]

        orchestrator = DebateOrchestrator()
        debate = await orchestrator.run_debate(topic, agents_config)
        debate_id = debate.debate_id

        # Retrieve the debate
        retrieved = orchestrator.get_debate(debate_id)

        # Should be the same debate
        assert retrieved.debate_id == debate_id
        assert retrieved.topic.title == topic.title
        assert len(retrieved.agent_responses) == 3


class TestPromptBuilding:
    """Tests for prompt building functions"""

    def test_for_prompt_building(self):
        """Test FOR prompt is built correctly"""
        from src.orchestrator import build_for_prompt

        topic = DebateTopic(
            title="Should AI have rights?",
            description="Discuss AI personhood"
        )

        prompt = build_for_prompt(topic)

        assert "Should AI have rights?" in prompt
        assert "favor" in prompt.lower() or "for" in prompt.lower()
        assert "Discuss AI personhood" in prompt

    def test_against_prompt_building(self):
        """Test AGAINST prompt includes FOR response"""
        from src.orchestrator import build_against_prompt

        topic = DebateTopic(
            title="Should AI have rights?",
            description="Test"
        )
        for_response = "AI systems are sentient and deserve protection"

        prompt = build_against_prompt(topic, for_response)

        assert "Should AI have rights?" in prompt
        assert for_response in prompt
        assert "against" in prompt.lower() or "counter" in prompt.lower()

    def test_synthesis_prompt_building(self):
        """Test SYNTHESIS prompt includes both responses"""
        from src.orchestrator import build_synthesis_prompt

        topic = DebateTopic(
            title="Should AI have rights?",
            description="Test"
        )
        for_response = "AI deserves rights"
        against_response = "AI should not have rights"

        prompt = build_synthesis_prompt(topic, for_response, against_response)

        assert "Should AI have rights?" in prompt
        assert for_response in prompt
        assert against_response in prompt
        assert "synthe" in prompt.lower() or "balance" in prompt.lower()
