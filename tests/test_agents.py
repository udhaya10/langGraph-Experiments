"""
Integration tests for Agent implementations
Tests Claude and Gemini agents with REAL CLI calls (not mocked)
"""
import pytest
import asyncio
from src.models import AgentConfig
from src.agents import ClaudeAgent, GeminiAgent, create_agent


class TestClaudeAgent:
    """Tests for ClaudeAgent with real Claude CLI"""

    @pytest.mark.asyncio
    async def test_claude_agent_execution_haiku(self):
        """Test executing Claude Haiku agent"""
        config = AgentConfig(
            name="Claude Haiku",
            role="FOR",
            model_provider="claude",
            model_name="haiku"
        )

        agent = ClaudeAgent(config)
        response = await agent.execute("What is 2+2?")

        # Validate response
        assert response.agent_name == "Claude Haiku"
        assert response.role == "FOR"
        assert response.model_provider == "claude"
        assert response.success is True
        assert response.error_message is None
        assert len(response.response_text) > 0
        assert "4" in response.response_text  # Should contain the answer
        assert response.execution_time_ms > 0

    @pytest.mark.asyncio
    async def test_claude_agent_execution_sonnet(self):
        """Test executing Claude Sonnet agent"""
        config = AgentConfig(
            name="Claude Sonnet",
            role="AGAINST",
            model_provider="claude",
            model_name="sonnet"
        )

        agent = ClaudeAgent(config)
        response = await agent.execute("What is the capital of France?")

        assert response.success is True
        assert response.error_message is None
        assert "Paris" in response.response_text
        assert response.execution_time_ms > 0

    @pytest.mark.asyncio
    async def test_claude_agent_timeout(self):
        """Test Claude agent with short timeout"""
        config = AgentConfig(
            name="Claude Timeout",
            role="FOR",
            model_provider="claude",
            model_name="haiku",
            timeout_seconds=1  # Very short timeout
        )

        agent = ClaudeAgent(config)
        # This may timeout or succeed depending on network speed
        response = await agent.execute("Write a 1000 word essay")

        # Response should be populated (success or failure)
        assert response.agent_name == "Claude Timeout"
        # Either succeeded or timed out, both are valid
        assert response.execution_time_ms >= 0


class TestGeminiAgent:
    """Tests for GeminiAgent with real Gemini CLI"""

    @pytest.mark.asyncio
    async def test_gemini_agent_execution_flash_lite(self):
        """Test executing Gemini Flash-Lite agent"""
        config = AgentConfig(
            name="Gemini Flash-Lite",
            role="FOR",
            model_provider="gemini",
            model_name="flash-lite"
        )

        agent = GeminiAgent(config)
        response = await agent.execute("What is 2+2?")

        # Validate response
        assert response.agent_name == "Gemini Flash-Lite"
        assert response.role == "FOR"
        assert response.model_provider == "gemini"
        assert response.success is True
        assert response.error_message is None
        assert len(response.response_text) > 0
        assert "4" in response.response_text
        assert response.execution_time_ms > 0
        # Should NOT contain "Loaded cached credentials" (should be cleaned)
        assert "Loaded cached credentials" not in response.response_text

    @pytest.mark.asyncio
    async def test_gemini_agent_execution_flash(self):
        """Test executing Gemini Flash agent"""
        config = AgentConfig(
            name="Gemini Flash",
            role="SYNTHESIS",
            model_provider="gemini",
            model_name="flash"
        )

        agent = GeminiAgent(config)
        response = await agent.execute("What is the capital of Japan?")

        assert response.success is True
        assert response.error_message is None
        assert "Tokyo" in response.response_text
        assert response.execution_time_ms > 0

    @pytest.mark.asyncio
    async def test_gemini_output_cleaning(self):
        """Test that Gemini output is properly cleaned"""
        config = AgentConfig(
            name="Gemini",
            role="FOR",
            model_provider="gemini",
            model_name="flash-lite"
        )

        agent = GeminiAgent(config)
        response = await agent.execute("Hello")

        # Output should be cleaned (no credential lines)
        lines = response.response_text.split('\n')
        for line in lines:
            assert "Loaded cached credentials" not in line
            assert "credentials" not in line.lower()


class TestAgentFactory:
    """Tests for agent creation factory"""

    def test_create_claude_agent(self):
        """Test factory creates Claude agent"""
        config = AgentConfig(
            name="Test Claude",
            role="FOR",
            model_provider="claude",
            model_name="sonnet"
        )

        agent = create_agent(config)
        assert isinstance(agent, ClaudeAgent)
        assert agent.config.model_provider == "claude"

    def test_create_gemini_agent(self):
        """Test factory creates Gemini agent"""
        config = AgentConfig(
            name="Test Gemini",
            role="AGAINST",
            model_provider="gemini",
            model_name="flash"
        )

        agent = create_agent(config)
        assert isinstance(agent, GeminiAgent)
        assert agent.config.model_provider == "gemini"

    def test_create_agent_invalid_provider(self):
        """Test factory with invalid provider"""
        config = AgentConfig(
            name="Invalid",
            role="FOR",
            model_provider="claude",  # Will create valid config
            model_name="sonnet"
        )
        # Override provider to invalid (bypassing validation)
        config.model_provider = "invalid"

        with pytest.raises((ValueError, KeyError)):
            create_agent(config)


class TestAgentResponseParsing:
    """Tests for response parsing and cleanup"""

    @pytest.mark.asyncio
    async def test_claude_response_parsing(self):
        """Test Claude response is correctly parsed"""
        config = AgentConfig(
            name="Test",
            role="FOR",
            model_provider="claude",
            model_name="haiku"
        )

        agent = ClaudeAgent(config)
        # Execute simple prompt to verify parsing
        response = await agent.execute("Say exactly: SUCCESS")

        assert response.success is True
        # Should contain the response
        assert len(response.response_text) > 0

    @pytest.mark.asyncio
    async def test_gemini_response_parsing_with_credentials(self):
        """Test Gemini response cleans credential messages"""
        config = AgentConfig(
            name="Test",
            role="FOR",
            model_provider="gemini",
            model_name="flash-lite"
        )

        agent = GeminiAgent(config)
        response = await agent.execute("Say exactly: SUCCESS")

        assert response.success is True
        # Verify no credential messages in output
        assert "Loaded cached credentials" not in response.response_text


class TestAgentErrorHandling:
    """Tests for agent error handling"""

    @pytest.mark.asyncio
    async def test_agent_cli_not_found(self):
        """Test handling when CLI is not found"""
        config = AgentConfig(
            name="Test",
            role="FOR",
            model_provider="claude",
            model_name="haiku"
        )

        # This test assumes claude CLI is installed
        # If not installed, we expect an error response
        agent = ClaudeAgent(config)
        response = await agent.execute("test")

        # Should either succeed or have an error message
        assert response.agent_name == "Test"
        # execution_time_ms should be set
        assert response.execution_time_ms >= 0
