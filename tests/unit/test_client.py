"""Unit tests for the main client."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from claude_cli_wrapper.core.client import run
from claude_cli_wrapper.errors import (
    AuthenticationError,
    CLINotFoundError,
    ExecutionError,
    TimeoutError,
)


def mock_subprocess_result(
    stdout: str = "response text",
    stderr: str = "",
    returncode: int = 0,
) -> MagicMock:
    """Create a mock subprocess result."""
    result = MagicMock()
    result.stdout = stdout
    result.stderr = stderr
    result.returncode = returncode
    return result


class TestRunBasic:
    """Tests for basic run() functionality."""

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_returns_claude_response(self, mock_run, mock_resolve) -> None:
        """run() should return a ClaudeResponse object."""
        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result(stdout="Hello!")

        response = run("Test prompt")

        assert response.text == "Hello!"
        assert response.exit_code == 0

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_passes_prompt_via_stdin(self, mock_run, mock_resolve) -> None:
        """run() should pass the prompt via stdin."""
        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result()

        run("My prompt text")

        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["input"] == "My prompt text"
        assert call_kwargs["text"] is True

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_captures_output(self, mock_run, mock_resolve) -> None:
        """run() should capture stdout and stderr."""
        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result(
            stdout="output",
            stderr="warnings",
        )

        response = run("Test")

        assert response.text == "output"
        assert response.stderr == "warnings"
        assert mock_run.call_args.kwargs["capture_output"] is True

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_uses_working_dir(self, mock_run, mock_resolve) -> None:
        """run() should use specified working directory."""
        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result()

        run("Test", working_dir="/custom/path")

        assert mock_run.call_args.kwargs["cwd"] == str(Path("/custom/path").resolve())

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_includes_working_dir_in_response(self, mock_run, mock_resolve) -> None:
        """run() should include working_dir in response."""
        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result()

        response = run("Test", working_dir="/test/dir")

        assert response.working_dir == str(Path("/test/dir").resolve())

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_includes_command_in_response(self, mock_run, mock_resolve) -> None:
        """run() should include the executed command in response."""
        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result()

        response = run("Test", model="opus")

        assert "claude" in response.command
        assert "--model" in response.command
        assert "opus" in response.command

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_measures_duration(self, mock_run, mock_resolve) -> None:
        """run() should measure execution duration."""
        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result()

        response = run("Test")

        assert response.duration >= 0
        assert isinstance(response.duration, float)


class TestRunWithModel:
    """Tests for run() with model parameter."""

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_passes_model_to_command(self, mock_run, mock_resolve) -> None:
        """run() should pass model to CLI."""
        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result()

        run("Test", model="opus")

        cmd = mock_run.call_args.args[0]
        assert "--model" in cmd
        assert "opus" in cmd


class TestRunWithTimeout:
    """Tests for run() with timeout parameter."""

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_passes_timeout_to_subprocess(self, mock_run, mock_resolve) -> None:
        """run() should pass timeout to subprocess."""
        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result()

        run("Test", timeout=30)

        assert mock_run.call_args.kwargs["timeout"] == 30

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_raises_timeout_error(self, mock_run, mock_resolve) -> None:
        """run() should raise TimeoutError when CLI times out."""
        mock_resolve.return_value = "claude"
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["claude"], timeout=30)

        with pytest.raises(TimeoutError) as exc_info:
            run("Test", timeout=30)

        assert exc_info.value.timeout == 30


class TestRunErrors:
    """Tests for run() error handling."""

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_raises_cli_not_found_error(self, mock_run, mock_resolve) -> None:
        """run() should raise CLINotFoundError when CLI not found."""
        mock_resolve.return_value = "claude"
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(CLINotFoundError):
            run("Test")

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_raises_authentication_error(self, mock_run, mock_resolve) -> None:
        """run() should raise AuthenticationError for auth failures."""
        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result(
            returncode=1,
            stderr="Error: not logged in",
        )

        with pytest.raises(AuthenticationError):
            run("Test")

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_raises_execution_error_for_nonzero_exit(
        self, mock_run, mock_resolve
    ) -> None:
        """run() should raise ExecutionError for non-zero exit codes."""
        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result(
            returncode=1,
            stderr="Some error",
        )

        with pytest.raises(ExecutionError) as exc_info:
            run("Test")

        assert exc_info.value.exit_code == 1
        assert "Some error" in exc_info.value.stderr


class TestRunWithResponseModel:
    """Tests for run() with response_model parameter."""

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_sets_json_output_format(self, mock_run, mock_resolve) -> None:
        """run() should use JSON output format when response_model is provided."""
        pytest.importorskip("pydantic")
        from pydantic import BaseModel

        class Person(BaseModel):
            name: str

        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result(stdout='{"name": "John"}')

        run("Extract name", response_model=Person)

        cmd = mock_run.call_args.args[0]
        assert "--output-format" in cmd
        idx = cmd.index("--output-format")
        assert cmd[idx + 1] == "json"

    @patch("claude_cli_wrapper.core.client.resolve_cli_path")
    @patch("claude_cli_wrapper.core.client.subprocess.run")
    def test_generates_json_schema_from_model(self, mock_run, mock_resolve) -> None:
        """run() should generate JSON schema from Pydantic model."""
        pytest.importorskip("pydantic")
        from pydantic import BaseModel

        class Item(BaseModel):
            value: int

        mock_resolve.return_value = "claude"
        mock_run.return_value = mock_subprocess_result(stdout='{"value": 42}')

        run("Extract value", response_model=Item)

        cmd = mock_run.call_args.args[0]
        assert "--json-schema" in cmd
