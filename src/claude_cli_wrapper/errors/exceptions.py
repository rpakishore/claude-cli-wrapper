"""Exception hierarchy for claude-cli-wrapper.

All exceptions inherit from ClaudeError, allowing users to catch all
wrapper-specific errors with a single except clause.
"""

from __future__ import annotations


class ClaudeError(Exception):
    """Base exception for all claude-cli-wrapper errors.

    Attributes:
        message: Human-readable error description.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class CLINotFoundError(ClaudeError):
    """Raised when the Claude CLI executable cannot be found.

    Attributes:
        message: Human-readable error description.
        cli_path: The path that was searched for the CLI.
    """

    def __init__(self, message: str, cli_path: str) -> None:
        self.cli_path = cli_path
        super().__init__(message)


class AuthenticationError(ClaudeError):
    """Raised when the user is not authenticated with the Claude CLI.

    This typically occurs when the user has not run 'claude' interactively
    to complete the authentication flow.

    Attributes:
        message: Human-readable error description.
    """

    pass


class InvalidArgumentError(ClaudeError):
    """Raised when invalid arguments are passed to the CLI.

    Attributes:
        message: Human-readable error description.
        argument: The name of the invalid argument (if known).
        value: The invalid value that was provided (if known).
    """

    def __init__(
        self,
        message: str,
        argument: str | None = None,
        value: str | None = None,
    ) -> None:
        self.argument = argument
        self.value = value
        super().__init__(message)


class TimeoutError(ClaudeError):
    """Raised when a CLI operation exceeds the specified timeout.

    Attributes:
        message: Human-readable error description.
        timeout: The timeout value in seconds that was exceeded.
        command: The command that timed out (if available).
    """

    def __init__(
        self,
        message: str,
        timeout: float,
        command: list[str] | None = None,
    ) -> None:
        self.timeout = timeout
        self.command = command
        super().__init__(message)


class ExecutionError(ClaudeError):
    """Raised when the CLI returns a non-zero exit code.

    This is a catch-all for CLI errors not covered by more specific exceptions.

    Attributes:
        message: Human-readable error description.
        exit_code: The non-zero exit code returned by the CLI.
        stderr: The stderr output from the CLI (if available).
        command: The command that failed (if available).
    """

    def __init__(
        self,
        message: str,
        exit_code: int,
        stderr: str | None = None,
        command: list[str] | None = None,
    ) -> None:
        self.exit_code = exit_code
        self.stderr = stderr
        self.command = command
        super().__init__(message)
