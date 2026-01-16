"""Agent model for custom subagents."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Agent:
    """Definition of a custom subagent for Claude CLI.

    Agents are specialized assistants with specific capabilities and instructions.

    Attributes:
        name: Unique identifier for the agent (used as key in JSON).
        description: Natural language description of when to use this agent.
        prompt: System prompt guiding the agent's behavior.
        tools: List of tools the agent can use. If None, inherits all tools.
        model: Model alias ('sonnet', 'opus', 'haiku'). If None, uses default.

    Example:
        >>> reviewer = Agent(
        ...     name="code-reviewer",
        ...     description="Expert code reviewer for Python",
        ...     prompt="You are a senior developer. Focus on code quality.",
        ...     tools=["Read", "Grep", "Glob"],
        ...     model="sonnet",
        ... )
    """

    name: str
    description: str
    prompt: str
    tools: list[str] | None = None
    model: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary format for CLI --agents flag.

        Returns:
            Dictionary with agent definition (excludes name, which is used as key).
        """
        result: dict = {
            "description": self.description,
            "prompt": self.prompt,
        }
        if self.tools is not None:
            result["tools"] = self.tools
        if self.model is not None:
            result["model"] = self.model
        return result
