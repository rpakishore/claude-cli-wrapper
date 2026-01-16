"""Unit tests for exception hierarchy."""

import pytest

from claude_cli_wrapper.errors import (
    AuthenticationError,
    ClaudeError,
    CLINotFoundError,
    ExecutionError,
    InvalidArgumentError,
    TimeoutError,
)


class TestClaudeError:
    """Tests for the base ClaudeError exception."""

    def test_inherits_from_exception(self) -> None:
        """ClaudeError should inherit from Exception."""
        assert issubclass(ClaudeError, Exception)

    def test_message_attribute(self) -> None:
        """ClaudeError should store the message."""
        error = ClaudeError("test message")
        assert error.message == "test message"
        assert str(error) == "test message"


class TestCLINotFoundError:
    """Tests for CLINotFoundError."""

    def test_inherits_from_claude_error(self) -> None:
        """CLINotFoundError should inherit from ClaudeError."""
        assert issubclass(CLINotFoundError, ClaudeError)

    def test_cli_path_attribute(self) -> None:
        """CLINotFoundError should store the cli_path."""
        error = CLINotFoundError("CLI not found", cli_path="/usr/bin/claude")
        assert error.cli_path == "/usr/bin/claude"
        assert error.message == "CLI not found"


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_inherits_from_claude_error(self) -> None:
        """AuthenticationError should inherit from ClaudeError."""
        assert issubclass(AuthenticationError, ClaudeError)


class TestInvalidArgumentError:
    """Tests for InvalidArgumentError."""

    def test_inherits_from_claude_error(self) -> None:
        """InvalidArgumentError should inherit from ClaudeError."""
        assert issubclass(InvalidArgumentError, ClaudeError)

    def test_optional_attributes(self) -> None:
        """InvalidArgumentError should store optional argument details."""
        error = InvalidArgumentError(
            "Invalid model",
            argument="model",
            value="invalid-model",
        )
        assert error.argument == "model"
        assert error.value == "invalid-model"

    def test_optional_attributes_default_to_none(self) -> None:
        """Optional attributes should default to None."""
        error = InvalidArgumentError("Invalid argument")
        assert error.argument is None
        assert error.value is None


class TestTimeoutError:
    """Tests for TimeoutError."""

    def test_inherits_from_claude_error(self) -> None:
        """TimeoutError should inherit from ClaudeError."""
        assert issubclass(TimeoutError, ClaudeError)

    def test_timeout_attribute(self) -> None:
        """TimeoutError should store the timeout value."""
        error = TimeoutError("Timed out", timeout=30.0)
        assert error.timeout == 30.0

    def test_command_attribute(self) -> None:
        """TimeoutError should store the command if provided."""
        error = TimeoutError(
            "Timed out",
            timeout=30.0,
            command=["claude", "-p", "test"],
        )
        assert error.command == ["claude", "-p", "test"]


class TestExecutionError:
    """Tests for ExecutionError."""

    def test_inherits_from_claude_error(self) -> None:
        """ExecutionError should inherit from ClaudeError."""
        assert issubclass(ExecutionError, ClaudeError)

    def test_exit_code_attribute(self) -> None:
        """ExecutionError should store the exit code."""
        error = ExecutionError("Failed", exit_code=1)
        assert error.exit_code == 1

    def test_stderr_attribute(self) -> None:
        """ExecutionError should store stderr output."""
        error = ExecutionError(
            "Failed",
            exit_code=1,
            stderr="Error: something went wrong",
        )
        assert error.stderr == "Error: something went wrong"

    def test_command_attribute(self) -> None:
        """ExecutionError should store the command if provided."""
        error = ExecutionError(
            "Failed",
            exit_code=1,
            command=["claude", "-p", "test"],
        )
        assert error.command == ["claude", "-p", "test"]


class TestExceptionHierarchy:
    """Tests for catching exceptions with base class."""

    def test_catch_all_with_claude_error(self) -> None:
        """All specific exceptions should be catchable with ClaudeError."""
        exceptions = [
            CLINotFoundError("not found", cli_path="/bin/claude"),
            AuthenticationError("not authenticated"),
            InvalidArgumentError("invalid"),
            TimeoutError("timeout", timeout=30.0),
            ExecutionError("failed", exit_code=1),
        ]

        for exc in exceptions:
            with pytest.raises(ClaudeError):
                raise exc
