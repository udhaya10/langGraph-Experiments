"""
Unit tests for Pydantic data models
Test-driven development: Tests written first, then implementation
"""
import pytest
from datetime import datetime
from src.models import AgentConfig, DebateTopic, AgentResponse, DebateRecord


class TestAgentConfig:
    """Tests for AgentConfig model"""

    def test_agent_config_creation_with_claude(self):
        """Test creating an AgentConfig for Claude agent"""
        config = AgentConfig(
            name="Claude FOR",
            role="FOR",
            model_provider="claude",
            model_name="sonnet",
            temperature=0.7,
            max_tokens=2000,
            timeout_seconds=60
        )
        assert config.name == "Claude FOR"
        assert config.role == "FOR"
        assert config.model_provider == "claude"
        assert config.model_name == "sonnet"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.timeout_seconds == 60
        # Model ID should be auto-generated
        assert config.model_id == "claude-sonnet-4-5-20250929"

    def test_agent_config_creation_with_gemini(self):
        """Test creating an AgentConfig for Gemini agent"""
        config = AgentConfig(
            name="Gemini AGAINST",
            role="AGAINST",
            model_provider="gemini",
            model_name="flash",
            temperature=0.8,
            max_tokens=1500,
            timeout_seconds=45
        )
        assert config.name == "Gemini AGAINST"
        assert config.role == "AGAINST"
        assert config.model_provider == "gemini"
        assert config.model_name == "flash"
        assert config.model_id == "gemini-2.5-flash"
        assert config.temperature == 0.8

    def test_agent_config_default_values(self):
        """Test that AgentConfig has correct default values"""
        config = AgentConfig(
            name="Agent 1",
            role="FOR",
            model_provider="claude",
            model_name="haiku"
        )
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.timeout_seconds == 60

    def test_agent_config_invalid_role(self):
        """Test that invalid role raises validation error"""
        with pytest.raises(ValueError):
            AgentConfig(
                name="Invalid",
                role="INVALID_ROLE",
                model_provider="claude",
                model_name="sonnet"
            )

    def test_agent_config_invalid_provider(self):
        """Test that invalid provider raises validation error"""
        with pytest.raises(ValueError):
            AgentConfig(
                name="Invalid",
                role="FOR",
                model_provider="invalid_provider",
                model_name="sonnet"
            )

    def test_agent_config_temperature_bounds(self):
        """Test that temperature must be between 0.0 and 1.0"""
        with pytest.raises(ValueError):
            AgentConfig(
                name="Agent 1",
                role="FOR",
                model_provider="claude",
                model_name="sonnet",
                temperature=1.5  # Invalid: > 1.0
            )

        with pytest.raises(ValueError):
            AgentConfig(
                name="Agent 1",
                role="FOR",
                model_provider="claude",
                model_name="sonnet",
                temperature=-0.1  # Invalid: < 0.0
            )


class TestDebateTopic:
    """Tests for DebateTopic model"""

    def test_debate_topic_creation(self):
        """Test creating a DebateTopic"""
        topic = DebateTopic(
            title="Should AI have legal rights?",
            description="Discuss whether AI systems should be granted legal personhood..."
        )
        assert topic.title == "Should AI have legal rights?"
        assert topic.description == "Discuss whether AI systems should be granted legal personhood..."

    def test_debate_topic_required_fields(self):
        """Test that title and description are required"""
        with pytest.raises(ValueError):
            DebateTopic(title="Only title")

        with pytest.raises(ValueError):
            DebateTopic(description="Only description")


class TestAgentResponse:
    """Tests for AgentResponse model"""

    def test_agent_response_successful(self):
        """Test creating a successful AgentResponse"""
        response = AgentResponse(
            agent_name="Claude FOR",
            role="FOR",
            model_provider="claude",
            model_name="sonnet",
            response_text="AI systems demonstrate emergent properties...",
            execution_time_ms=2300,
            success=True,
            error_message=None
        )
        assert response.agent_name == "Claude FOR"
        assert response.role == "FOR"
        assert response.success is True
        assert response.error_message is None
        assert response.execution_time_ms == 2300

    def test_agent_response_failed(self):
        """Test creating a failed AgentResponse"""
        response = AgentResponse(
            agent_name="Claude FOR",
            role="FOR",
            model_provider="claude",
            model_name="sonnet",
            response_text="",
            execution_time_ms=0,
            success=False,
            error_message="Timeout: Claude CLI did not respond"
        )
        assert response.success is False
        assert response.error_message == "Timeout: Claude CLI did not respond"

    def test_agent_response_invalid_role(self):
        """Test that invalid role raises validation error"""
        with pytest.raises(ValueError):
            AgentResponse(
                agent_name="Agent 1",
                role="INVALID",
                model_provider="claude",
                model_name="sonnet",
                response_text="test",
                execution_time_ms=100,
                success=True
            )


class TestDebateRecord:
    """Tests for DebateRecord model"""

    def test_debate_record_creation(self):
        """Test creating a DebateRecord with responses"""
        topic = DebateTopic(
            title="Should AI have legal rights?",
            description="Test topic"
        )

        agent_config = AgentConfig(
            name="Claude FOR",
            role="FOR",
            model_provider="claude",
            model_name="sonnet"
        )

        response = AgentResponse(
            agent_name="Claude FOR",
            role="FOR",
            model_provider="claude",
            model_name="sonnet",
            response_text="AI should have rights",
            execution_time_ms=2300,
            success=True
        )

        debate = DebateRecord(
            topic=topic,
            agents_config=[agent_config],
            agent_responses=[response],
            total_execution_time_ms=2300
        )

        assert debate.topic.title == "Should AI have legal rights?"
        assert len(debate.agents_config) == 1
        assert len(debate.agent_responses) == 1
        assert debate.total_execution_time_ms == 2300
        assert debate.debate_id is not None  # Should have auto-generated UUID
        assert debate.created_at is not None

    def test_debate_record_empty_responses(self):
        """Test creating a DebateRecord with empty responses"""
        topic = DebateTopic(
            title="Test",
            description="Test topic"
        )

        debate = DebateRecord(
            topic=topic,
            agents_config=[],
            agent_responses=[],
            total_execution_time_ms=0
        )

        assert len(debate.agent_responses) == 0
        assert debate.debate_id is not None

    def test_debate_record_multiple_agents(self):
        """Test DebateRecord with multiple agents (FOR, AGAINST, SYNTHESIS)"""
        topic = DebateTopic(
            title="Should AI have legal rights?",
            description="Test topic"
        )

        agents_config = [
            AgentConfig(name="Agent 1", role="FOR", model_provider="claude", model_name="sonnet"),
            AgentConfig(name="Agent 2", role="AGAINST", model_provider="gemini", model_name="flash"),
            AgentConfig(name="Agent 3", role="SYNTHESIS", model_provider="claude", model_name="opus"),
        ]

        responses = [
            AgentResponse(agent_name="Agent 1", role="FOR", model_provider="claude", model_name="sonnet", response_text="For", execution_time_ms=1000, success=True),
            AgentResponse(agent_name="Agent 2", role="AGAINST", model_provider="gemini", model_name="flash", response_text="Against", execution_time_ms=1200, success=True),
            AgentResponse(agent_name="Agent 3", role="SYNTHESIS", model_provider="claude", model_name="opus", response_text="Synthesis", execution_time_ms=1500, success=True),
        ]

        debate = DebateRecord(
            topic=topic,
            agents_config=agents_config,
            agent_responses=responses,
            total_execution_time_ms=3700
        )

        assert len(debate.agents_config) == 3
        assert len(debate.agent_responses) == 3
        assert debate.total_execution_time_ms == 3700
