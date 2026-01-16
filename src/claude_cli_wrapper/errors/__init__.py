"""Error handling for claude-cli-wrapper."""

from claude_cli_wrapper.errors.exceptions import (
    AuthenticationError,
    ClaudeError,
    CLINotFoundError,
    ExecutionError,
    InvalidArgumentError,
    TimeoutError,
)

__all__ = [
    "ClaudeError",
    "CLINotFoundError",
    "AuthenticationError",
    "InvalidArgumentError",
    "TimeoutError",
    "ExecutionError",
]
