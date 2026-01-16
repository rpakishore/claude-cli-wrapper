"""Claude CLI Wrapper - A Python wrapper for the Claude Code CLI.

This package provides a clean Python interface for interacting with Claude
via the Claude Code CLI, enabling programmatic access without API keys.

Example:
    >>> from claude_cli_wrapper import run
    >>> response = run("Explain Python decorators")
    >>> print(response.text)

    >>> from claude_cli_wrapper import claude_session
    >>> with claude_session() as session:
    ...     r1 = session.run("What is Python?")
    ...     r2 = session.run("Give me an example")
"""

from claude_cli_wrapper.core import ClaudeResponse, Session, claude_session, run
from claude_cli_wrapper.errors import (
    AuthenticationError,
    ClaudeError,
    CLINotFoundError,
    ExecutionError,
    InvalidArgumentError,
    TimeoutError,
)
from claude_cli_wrapper.models import Agent, Model, OutputFormat, PermissionMode

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Main function
    "run",
    # Session management
    "claude_session",
    "Session",
    # Response
    "ClaudeResponse",
    # Exceptions
    "ClaudeError",
    "CLINotFoundError",
    "AuthenticationError",
    "InvalidArgumentError",
    "TimeoutError",
    "ExecutionError",
    # Models/Enums
    "Agent",
    "Model",
    "OutputFormat",
    "PermissionMode",
]
