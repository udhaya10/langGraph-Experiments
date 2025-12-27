"""
Pydantic data models for the debate system
Defines the core data structures used throughout the application
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime
from uuid import uuid4


class AgentConfig(BaseModel):
    """Configuration for a debate agent (Claude or Gemini)"""

    name: str = Field(..., description="Agent name (e.g., 'Claude FOR')")
    role: Literal["FOR", "AGAINST", "SYNTHESIS"] = Field(..., description="Agent role in debate")
    model_provider: Literal["claude", "gemini"] = Field(..., description="AI provider")
    model_name: str = Field(..., description="Model name (e.g., 'sonnet', 'flash')")
    model_id: str = Field(default="", description="Full model ID (auto-generated)")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Temperature for generation")
    max_tokens: int = Field(default=2000, gt=0, description="Max tokens to generate")
    timeout_seconds: int = Field(default=60, gt=0, description="CLI execution timeout")

    def model_post_init(self, __context):
        """Auto-generate model_id after model initialization"""
        if not self.model_id:
            # Map model names to full model IDs
            if self.model_provider == "claude":
                model_map = {
                    "haiku": "claude-haiku-4-5-20251001",
                    "sonnet": "claude-sonnet-4-5-20250929",
                    "opus": "claude-opus-4-5-20251101",
                }
                self.model_id = model_map.get(self.model_name, f"claude-{self.model_name}")

            elif self.model_provider == "gemini":
                model_map = {
                    "flash-lite": "gemini-2.5-flash-lite",
                    "flash": "gemini-2.5-flash",
                    "pro": "gemini-2.5-pro",
                }
                self.model_id = model_map.get(self.model_name, f"gemini-{self.model_name}")


class DebateTopic(BaseModel):
    """Topic for a debate"""

    title: str = Field(..., description="Debate topic title")
    description: str = Field(..., description="Detailed description of the topic")


class AgentResponse(BaseModel):
    """Response from an agent execution"""

    agent_name: str = Field(..., description="Name of the agent")
    role: Literal["FOR", "AGAINST", "SYNTHESIS"] = Field(..., description="Role of the agent")
    model_provider: str = Field(..., description="AI provider (claude/gemini)")
    model_name: str = Field(..., description="Model name")
    response_text: str = Field(default="", description="The actual response text")
    execution_time_ms: float = Field(default=0, ge=0, description="Execution time in milliseconds")
    success: bool = Field(default=False, description="Whether execution was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")


class DebateRecord(BaseModel):
    """Complete record of a debate"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "debate_id": "550e8400-e29b-41d4-a716-446655440000",
                "topic": {
                    "title": "Should AI have legal rights?",
                    "description": "Discuss whether AI systems should be granted legal personhood..."
                },
                "agents_config": [
                    {
                        "name": "Claude FOR",
                        "role": "FOR",
                        "model_provider": "claude",
                        "model_name": "sonnet",
                        "model_id": "claude-sonnet-4-5-20250929",
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "timeout_seconds": 60
                    }
                ],
                "agent_responses": [
                    {
                        "agent_name": "Claude FOR",
                        "role": "FOR",
                        "model_provider": "claude",
                        "model_name": "sonnet",
                        "response_text": "AI systems demonstrate emergent properties...",
                        "execution_time_ms": 2300,
                        "success": True,
                        "error_message": None
                    }
                ],
                "total_execution_time_ms": 2300,
                "created_at": "2025-01-15T10:00:00"
            }
        }
    )

    debate_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique debate ID")
    topic: DebateTopic = Field(..., description="Debate topic")
    agents_config: List[AgentConfig] = Field(default_factory=list, description="Agent configurations")
    agent_responses: List[AgentResponse] = Field(default_factory=list, description="Agent responses")
    total_execution_time_ms: float = Field(default=0, ge=0, description="Total execution time")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
