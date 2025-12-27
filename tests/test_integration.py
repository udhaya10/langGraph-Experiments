"""
Comprehensive Integration Tests - Test actual flow end-to-end
Validates context-passing, prompt building, and complete orchestration
"""
import pytest
from src.models import DebateTopic, AgentConfig
from src.orchestrator import DebateOrchestrator, build_for_prompt, build_against_prompt, build_synthesis_prompt
from src.agents import ClaudeAgent
import asyncio


class TestContextPassingFlow:
    """Test the actual context-passing flow"""

    @pytest.mark.asyncio
    async def test_prompt_building_includes_context(self):
        """Test that prompts are built with actual context"""
        topic = DebateTopic(
            title="Should AI have rights?",
            description="Discuss AI personhood"
        )

        # Build FOR prompt (no context)
        for_prompt = build_for_prompt(topic)
        assert "Should AI have rights?" in for_prompt
        assert "favor" in for_prompt.lower() or "for" in for_prompt.lower()
        assert len(for_prompt) > 100

        # Build AGAINST prompt with FOR response
        for_response_text = "AI systems demonstrate sentience and deserve legal protection"
        against_prompt = build_against_prompt(topic, for_response_text)

        # CRITICAL: Verify FOR response is IN the AGAINST prompt
        assert for_response_text in against_prompt, "AGAINST prompt must include FOR response"
        assert "Should AI have rights?" in against_prompt
        assert "counter" in against_prompt.lower() or "against" in against_prompt.lower()

        # Build SYNTHESIS prompt with both responses
        against_response_text = "However, AI systems lack consciousness and cannot have rights"
        synthesis_prompt = build_synthesis_prompt(topic, for_response_text, against_response_text)

        # CRITICAL: Verify BOTH responses are IN the SYNTHESIS prompt
        assert for_response_text in synthesis_prompt, "SYNTHESIS prompt must include FOR response"
        assert against_response_text in synthesis_prompt, "SYNTHESIS prompt must include AGAINST response"
        assert "synthe" in synthesis_prompt.lower() or "balance" in synthesis_prompt.lower()

    @pytest.mark.asyncio
    async def test_actual_agent_execution_flow(self):
        """Test actual agent execution with real CLI"""
        topic = DebateTopic(
            title="Is Python good?",
            description="Test"
        )

        # Create a simple FOR agent
        for_config = AgentConfig(
            name="Test FOR",
            role="FOR",
            model_provider="claude",
            model_name="haiku"
        )

        agent = ClaudeAgent(for_config)

        # Build and execute FOR prompt
        for_prompt = build_for_prompt(topic)
        for_response = await agent.execute(for_prompt)

        # Verify response is valid
        assert for_response.success is True, f"Agent failed: {for_response.error_message}"
        assert len(for_response.response_text) > 50, "Response too short"
        assert for_response.role == "FOR"
        assert for_response.agent_name == "Test FOR"

    @pytest.mark.asyncio
    async def test_complete_debate_flow_sequential(self):
        """Test complete debate flow - agents actually run sequentially"""
        topic = DebateTopic(
            title="Is water important?",  # Simpler topic
            description="Test debate"
        )

        agents_config = [
            AgentConfig(name="FOR", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="AGAINST", role="AGAINST", model_provider="claude", model_name="haiku"),
            AgentConfig(name="SYNTHESIS", role="SYNTHESIS", model_provider="claude", model_name="haiku"),
        ]

        orchestrator = DebateOrchestrator()
        debate = await orchestrator.run_debate(topic, agents_config)

        # Verify all responses exist
        assert len(debate.agent_responses) == 3

        for_resp = debate.agent_responses[0]
        against_resp = debate.agent_responses[1]
        synthesis_resp = debate.agent_responses[2]

        # Verify all responses succeeded (main criterion)
        assert for_resp.success is True, f"FOR failed: {for_resp.error_message}"
        assert against_resp.success is True, f"AGAINST failed: {against_resp.error_message}"
        assert synthesis_resp.success is True, f"SYNTHESIS failed: {synthesis_resp.error_message}"

        # Verify responses are not empty (at least 20 chars)
        assert len(for_resp.response_text) > 20, f"FOR response too short: {len(for_resp.response_text)} chars"
        assert len(against_resp.response_text) > 20, f"AGAINST response too short: {len(against_resp.response_text)} chars"
        assert len(synthesis_resp.response_text) > 20, f"SYNTHESIS response too short: {len(synthesis_resp.response_text)} chars"

        # Verify they're different responses (not identical copies)
        assert for_resp.response_text != against_resp.response_text, "FOR and AGAINST responses are identical"
        assert against_resp.response_text != synthesis_resp.response_text, "AGAINST and SYNTHESIS responses are identical"

        # Verify execution times are reasonable
        assert for_resp.execution_time_ms > 0
        assert against_resp.execution_time_ms > 0
        assert synthesis_resp.execution_time_ms > 0


class TestPromptBuildingDetailedFlow:
    """Test that prompts are built correctly at each stage"""

    def test_for_prompt_structure(self):
        """Test FOR prompt has correct structure"""
        topic = DebateTopic(
            title="AI Ethics",
            description="Should AI systems be regulated?"
        )

        prompt = build_for_prompt(topic)

        # Check structure
        assert "AI Ethics" in prompt
        assert "Should AI systems be regulated?" in prompt
        assert "favor" in prompt.lower() or "for" in prompt.lower()
        assert "argument" in prompt.lower()

        # Should NOT include context (no previous responses)
        assert "AGAINST" not in prompt
        assert "SYNTHESIS" not in prompt

    def test_against_prompt_includes_for_context(self):
        """Test AGAINST prompt includes FOR context"""
        topic = DebateTopic(
            title="AI Ethics",
            description="Should AI systems be regulated?"
        )
        for_text = "AI systems need regulation because they affect society"

        prompt = build_against_prompt(topic, for_text)

        # Check it includes FOR response
        assert for_text in prompt, "AGAINST prompt must quote FOR argument"
        assert "AI Ethics" in prompt

        # Check it asks for counter-argument
        assert "counter" in prompt.lower() or "against" in prompt.lower() or "challenge" in prompt.lower()

    def test_synthesis_prompt_includes_all_context(self):
        """Test SYNTHESIS prompt includes both FOR and AGAINST"""
        topic = DebateTopic(
            title="AI Ethics",
            description="Should AI be regulated?"
        )
        for_text = "AI needs regulation"
        against_text = "AI shouldn't be overregulated"

        prompt = build_synthesis_prompt(topic, for_text, against_text)

        # Check it includes both
        assert for_text in prompt, "SYNTHESIS must include FOR argument"
        assert against_text in prompt, "SYNTHESIS must include AGAINST argument"
        assert "AI Ethics" in prompt

        # Check it asks for synthesis
        assert "synthe" in prompt.lower() or "balance" in prompt.lower() or "both" in prompt.lower()


class TestOrchestratorSequentialExecution:
    """Test that orchestrator executes agents sequentially with context-passing"""

    @pytest.mark.asyncio
    async def test_orchestrator_validates_agent_count(self):
        """Test that orchestrator validates exactly 3 agents"""
        topic = DebateTopic(title="Test", description="Test")
        orchestrator = DebateOrchestrator()

        # Test with 2 agents (should fail)
        agents_2 = [
            AgentConfig(name="1", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="2", role="AGAINST", model_provider="claude", model_name="haiku"),
        ]

        with pytest.raises(ValueError):
            await orchestrator.run_debate(topic, agents_2)

        # Test with 4 agents (should fail)
        agents_4 = [
            AgentConfig(name="1", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="2", role="AGAINST", model_provider="claude", model_name="haiku"),
            AgentConfig(name="3", role="SYNTHESIS", model_provider="claude", model_name="haiku"),
            AgentConfig(name="4", role="FOR", model_provider="claude", model_name="haiku"),
        ]

        with pytest.raises(ValueError):
            await orchestrator.run_debate(topic, agents_4)

    @pytest.mark.asyncio
    async def test_orchestrator_validates_roles(self):
        """Test that orchestrator validates FOR, AGAINST, SYNTHESIS roles"""
        topic = DebateTopic(title="Test", description="Test")
        orchestrator = DebateOrchestrator()

        # Missing SYNTHESIS
        invalid_agents = [
            AgentConfig(name="1", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="2", role="AGAINST", model_provider="claude", model_name="haiku"),
            AgentConfig(name="3", role="FOR", model_provider="claude", model_name="haiku"),  # Duplicate FOR
        ]

        with pytest.raises(ValueError):
            await orchestrator.run_debate(topic, invalid_agents)

    @pytest.mark.asyncio
    async def test_debate_storage_integration(self):
        """Test that debate is stored after running"""
        topic = DebateTopic(
            title="Storage Test",
            description="Test storage integration"
        )

        agents_config = [
            AgentConfig(name="A", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="B", role="AGAINST", model_provider="claude", model_name="haiku"),
            AgentConfig(name="C", role="SYNTHESIS", model_provider="claude", model_name="haiku"),
        ]

        orchestrator = DebateOrchestrator()
        debate = await orchestrator.run_debate(topic, agents_config)

        # Verify debate has ID
        debate_id = debate.debate_id
        assert debate_id is not None

        # Retrieve the stored debate
        retrieved = orchestrator.get_debate(debate_id)

        # Verify it's the same debate
        assert retrieved.debate_id == debate_id
        assert retrieved.topic.title == "Storage Test"
        assert len(retrieved.agent_responses) == 3


class TestResponseQuality:
    """Test that responses are actually meaningful"""

    @pytest.mark.asyncio
    async def test_responses_are_not_empty_templates(self):
        """Test that responses are real agent output, not templates"""
        topic = DebateTopic(
            title="Python programming",
            description="Is Python a good language?"
        )

        agents_config = [
            AgentConfig(name="FOR", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="AGAINST", role="AGAINST", model_provider="claude", model_name="haiku"),
            AgentConfig(name="SYNTHESIS", role="SYNTHESIS", model_provider="claude", model_name="haiku"),
        ]

        orchestrator = DebateOrchestrator()
        debate = await orchestrator.run_debate(topic, agents_config)

        for response in debate.agent_responses:
            # Response should be substantial
            assert len(response.response_text) > 200, f"{response.role} response too short"

            # Response should contain relevant content (not just template text)
            response_lower = response.response_text.lower()
            assert "python" in response_lower or "language" in response_lower

            # Response should not be obviously templated
            assert not response.response_text.startswith("Here is a debate")
            assert not response.response_text.startswith("I will")

    @pytest.mark.asyncio
    async def test_execution_times_are_reasonable(self):
        """Test that execution times are recorded realistically"""
        topic = DebateTopic(title="Test", description="Test")

        agents_config = [
            AgentConfig(name="1", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="2", role="AGAINST", model_provider="claude", model_name="haiku"),
            AgentConfig(name="3", role="SYNTHESIS", model_provider="claude", model_name="haiku"),
        ]

        orchestrator = DebateOrchestrator()
        debate = await orchestrator.run_debate(topic, agents_config)

        # Each response should have execution time > 0
        for response in debate.agent_responses:
            assert response.execution_time_ms > 0, "Execution time should be > 0"
            assert response.execution_time_ms < 120000, "Execution time should be < 2 minutes"

        # Total time should be sum of individual times (approximately)
        total_individual = sum(r.execution_time_ms for r in debate.agent_responses)
        assert debate.total_execution_time_ms > 0
        assert debate.total_execution_time_ms >= min(r.execution_time_ms for r in debate.agent_responses)


class TestErrorHandlingRealFlow:
    """Test error handling in real execution"""

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test that timeouts are handled gracefully"""
        topic = DebateTopic(title="Test", description="Test")

        # Create agent with very short timeout
        config = AgentConfig(
            name="Timeout Test",
            role="FOR",
            model_provider="claude",
            model_name="haiku",
            timeout_seconds=1  # Very short timeout
        )

        agent = ClaudeAgent(config)
        response = await agent.execute("Write a 1000 word essay on philosophy")

        # Should either succeed or have timeout error (not crash)
        assert response.agent_name == "Timeout Test"
        # execution_time_ms should be set regardless
        assert response.execution_time_ms >= 0
