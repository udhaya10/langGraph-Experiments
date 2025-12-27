"""
Agent implementations for Claude and Gemini CLIs
Handles subprocess execution and response parsing
"""
import subprocess
import asyncio
import time
from abc import ABC, abstractmethod
from src.models import AgentConfig, AgentResponse


class Agent(ABC):
    """Abstract base class for all agents"""

    def __init__(self, config: AgentConfig):
        """Initialize agent with configuration"""
        self.config = config

    @abstractmethod
    async def execute(self, prompt: str) -> AgentResponse:
        """
        Execute the agent with a prompt
        Returns AgentResponse with result
        """
        pass

    @abstractmethod
    def _build_command(self, prompt: str) -> list:
        """Build CLI command for this agent"""
        pass

    async def _execute_subprocess(self, command: list) -> tuple[str, str, float]:
        """
        Execute subprocess command asynchronously
        Returns: (stdout, stderr, execution_time_ms)
        """
        start_time = time.time()

        try:
            # Run subprocess with timeout
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.timeout_seconds
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                execution_time = (time.time() - start_time) * 1000
                raise TimeoutError(
                    f"Agent {self.config.name} timed out after {self.config.timeout_seconds}s"
                )

            execution_time = (time.time() - start_time) * 1000
            stdout_str = stdout.decode('utf-8', errors='replace')
            stderr_str = stderr.decode('utf-8', errors='replace')

            return stdout_str, stderr_str, execution_time

        except FileNotFoundError:
            execution_time = (time.time() - start_time) * 1000
            raise RuntimeError(f"CLI command not found: {command[0]}")

    def _parse_response(self, stdout: str, stderr: str, execution_time_ms: float) -> AgentResponse:
        """Parse CLI output into AgentResponse"""
        response_text = stdout.strip() if stdout else ""

        return AgentResponse(
            agent_name=self.config.name,
            role=self.config.role,
            model_provider=self.config.model_provider,
            model_name=self.config.model_name,
            response_text=response_text,
            execution_time_ms=execution_time_ms,
            success=True,
            error_message=None
        )


class ClaudeAgent(Agent):
    """Claude CLI agent implementation"""

    def _build_command(self, prompt: str) -> list:
        """Build claude CLI command"""
        return [
            "claude",
            "--model", self.config.model_id,
            "--print", prompt
        ]

    async def execute(self, prompt: str) -> AgentResponse:
        """Execute Claude agent"""
        try:
            command = self._build_command(prompt)
            stdout, stderr, execution_time = await self._execute_subprocess(command)
            return self._parse_response(stdout, stderr, execution_time)

        except TimeoutError as e:
            return AgentResponse(
                agent_name=self.config.name,
                role=self.config.role,
                model_provider=self.config.model_provider,
                model_name=self.config.model_name,
                response_text="",
                execution_time_ms=self.config.timeout_seconds * 1000,
                success=False,
                error_message=str(e)
            )

        except Exception as e:
            return AgentResponse(
                agent_name=self.config.name,
                role=self.config.role,
                model_provider=self.config.model_provider,
                model_name=self.config.model_name,
                response_text="",
                execution_time_ms=0,
                success=False,
                error_message=str(e)
            )


class GeminiAgent(Agent):
    """Gemini CLI agent implementation"""

    def _build_command(self, prompt: str) -> list:
        """Build gemini CLI command"""
        return [
            "gemini",
            "--yolo",
            "-m", self.config.model_id,
            prompt
        ]

    def _clean_gemini_output(self, text: str) -> str:
        """Remove credential lines from Gemini output"""
        lines = text.split('\n')
        cleaned_lines = [
            line for line in lines
            if "Loaded cached credentials" not in line
            and "credentials" not in line.lower()
        ]
        return '\n'.join(cleaned_lines).strip()

    def _parse_response(self, stdout: str, stderr: str, execution_time_ms: float) -> AgentResponse:
        """Parse Gemini CLI output, removing credential messages"""
        response_text = self._clean_gemini_output(stdout) if stdout else ""

        return AgentResponse(
            agent_name=self.config.name,
            role=self.config.role,
            model_provider=self.config.model_provider,
            model_name=self.config.model_name,
            response_text=response_text,
            execution_time_ms=execution_time_ms,
            success=True,
            error_message=None
        )

    async def execute(self, prompt: str) -> AgentResponse:
        """Execute Gemini agent"""
        try:
            command = self._build_command(prompt)
            stdout, stderr, execution_time = await self._execute_subprocess(command)
            return self._parse_response(stdout, stderr, execution_time)

        except TimeoutError as e:
            return AgentResponse(
                agent_name=self.config.name,
                role=self.config.role,
                model_provider=self.config.model_provider,
                model_name=self.config.model_name,
                response_text="",
                execution_time_ms=self.config.timeout_seconds * 1000,
                success=False,
                error_message=str(e)
            )

        except Exception as e:
            return AgentResponse(
                agent_name=self.config.name,
                role=self.config.role,
                model_provider=self.config.model_provider,
                model_name=self.config.model_name,
                response_text="",
                execution_time_ms=0,
                success=False,
                error_message=str(e)
            )


def create_agent(config: AgentConfig) -> Agent:
    """Factory function to create agents based on config"""
    if config.model_provider == "claude":
        return ClaudeAgent(config)
    elif config.model_provider == "gemini":
        return GeminiAgent(config)
    else:
        raise ValueError(f"Unknown provider: {config.model_provider}")
