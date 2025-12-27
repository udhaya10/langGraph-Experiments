"""
Tests for CLI interface
Tests Click commands for running and managing debates
"""
import pytest
from click.testing import CliRunner
from src.cli import cli_group, debate_command, debates_list_command, debates_view_command, debates_export_command
from src.models import DebateTopic, AgentConfig
from src.orchestrator import DebateOrchestrator
import asyncio


@pytest.fixture
def cli_runner():
    """Create CLI runner for testing"""
    return CliRunner()


@pytest.fixture
def sample_debate():
    """Create a sample debate for testing"""
    async def create():
        topic = DebateTopic(
            title="Test debate topic",
            description="A test debate for CLI testing"
        )
        agents = [
            AgentConfig(name="Agent 1", role="FOR", model_provider="claude", model_name="haiku"),
            AgentConfig(name="Agent 2", role="AGAINST", model_provider="claude", model_name="haiku"),
            AgentConfig(name="Agent 3", role="SYNTHESIS", model_provider="claude", model_name="haiku"),
        ]
        orchestrator = DebateOrchestrator()
        debate = await orchestrator.run_debate(topic, agents)
        return debate

    return asyncio.run(create())


class TestDebateCommand:
    """Tests for debate command"""

    def test_debate_command_help(self, cli_runner):
        """Test debate command help"""
        result = cli_runner.invoke(debate_command, ['--help'])
        assert result.exit_code == 0
        assert '--topic' in result.output
        assert '--description' in result.output
        assert '--output' in result.output or 'output' in result.output.lower()

    def test_debate_command_missing_args(self, cli_runner):
        """Test debate command with missing required arguments"""
        result = cli_runner.invoke(debate_command, [])
        assert result.exit_code != 0

    def test_debate_command_with_topic_only(self, cli_runner):
        """Test debate command with topic but no description"""
        result = cli_runner.invoke(debate_command, [
            '--topic', 'Test topic'
        ])
        # Should fail because description is missing
        assert result.exit_code != 0

    def test_debate_command_run_debate(self, cli_runner):
        """Test running a debate via CLI"""
        result = cli_runner.invoke(debate_command, [
            '--topic', 'Is Python good?',
            '--description', 'Test debate about Python'
        ])
        # Should succeed
        assert result.exit_code == 0
        # Output should contain debate results
        assert 'Debate' in result.output or 'debate' in result.output.lower()


class TestDebatesListCommand:
    """Tests for debates list command"""

    def test_debates_list_help(self, cli_runner):
        """Test debates list command help"""
        result = cli_runner.invoke(debates_list_command, ['--help'])
        assert result.exit_code == 0

    def test_debates_list_default(self, cli_runner):
        """Test listing debates with default limit"""
        result = cli_runner.invoke(debates_list_command, [])
        assert result.exit_code == 0
        # Should show some output (even if no debates)
        assert len(result.output) > 0

    def test_debates_list_with_limit(self, cli_runner):
        """Test listing debates with custom limit"""
        result = cli_runner.invoke(debates_list_command, [
            '--limit', '5'
        ])
        assert result.exit_code == 0


class TestDebatesViewCommand:
    """Tests for debates view command"""

    def test_debates_view_help(self, cli_runner):
        """Test debates view command help"""
        result = cli_runner.invoke(debates_view_command, ['--help'])
        assert result.exit_code == 0

    def test_debates_view_missing_id(self, cli_runner):
        """Test view without debate ID"""
        result = cli_runner.invoke(debates_view_command, [])
        # Should fail because debate_id is required
        assert result.exit_code != 0

    def test_debates_view_invalid_id(self, cli_runner):
        """Test view with invalid debate ID"""
        result = cli_runner.invoke(debates_view_command, [
            'invalid-debate-id-12345'
        ])
        # Should fail (debate not found)
        assert result.exit_code != 0

    def test_debates_view_with_valid_id(self, cli_runner, sample_debate):
        """Test view with valid debate ID"""
        result = cli_runner.invoke(debates_view_command, [
            sample_debate.debate_id
        ])
        # Should succeed
        assert result.exit_code == 0
        # Output should contain debate info
        assert sample_debate.topic.title in result.output


class TestDebatesExportCommand:
    """Tests for debates export command"""

    def test_debates_export_help(self, cli_runner):
        """Test debates export command help"""
        result = cli_runner.invoke(debates_export_command, ['--help'])
        assert result.exit_code == 0

    def test_debates_export_missing_id(self, cli_runner):
        """Test export without debate ID"""
        result = cli_runner.invoke(debates_export_command, [])
        assert result.exit_code != 0

    def test_debates_export_invalid_id(self, cli_runner):
        """Test export with invalid debate ID"""
        result = cli_runner.invoke(debates_export_command, [
            'invalid-id'
        ])
        # Should fail (debate not found)
        assert result.exit_code != 0

    def test_debates_export_valid_debate(self, cli_runner, sample_debate):
        """Test exporting a valid debate"""
        result = cli_runner.invoke(debates_export_command, [
            sample_debate.debate_id,
            '--output', '/tmp/test_debate.md',
            '--format', 'markdown'
        ])
        # Should succeed
        assert result.exit_code == 0
        # File should be created
        import os
        assert os.path.exists('/tmp/test_debate.md')
        # Clean up
        os.remove('/tmp/test_debate.md')


class TestCLIGroup:
    """Tests for main CLI group"""

    def test_cli_help(self, cli_runner):
        """Test main CLI help"""
        result = cli_runner.invoke(cli_group, ['--help'])
        assert result.exit_code == 0
        assert 'debate' in result.output.lower()
        assert 'debates' in result.output.lower()

    def test_cli_no_command(self, cli_runner):
        """Test CLI with no command"""
        result = cli_runner.invoke(cli_group, [])
        # Click returns exit code 2 when no command is provided
        assert result.exit_code in [0, 2]
