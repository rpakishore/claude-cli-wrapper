"""Shared mock responses for tests."""

from unittest.mock import MagicMock


def create_mock_subprocess_result(
    stdout: str = "mock response",
    stderr: str = "",
    returncode: int = 0,
) -> MagicMock:
    """Create a mock subprocess.CompletedProcess result.

    Args:
        stdout: The stdout content.
        stderr: The stderr content.
        returncode: The process return code.

    Returns:
        A MagicMock configured as a CompletedProcess.
    """
    result = MagicMock()
    result.stdout = stdout
    result.stderr = stderr
    result.returncode = returncode
    return result


def create_mock_claude_response(
    text: str = "mock response",
    exit_code: int = 0,
    stderr: str = "",
    command: list[str] | None = None,
    working_dir: str = "/tmp",
    duration: float = 1.0,
) -> MagicMock:
    """Create a mock ClaudeResponse object.

    Args:
        text: The response text.
        exit_code: The exit code.
        stderr: Any stderr output.
        command: The command that was run.
        working_dir: The working directory.
        duration: The execution duration.

    Returns:
        A MagicMock configured as a ClaudeResponse.
    """
    if command is None:
        command = ["claude", "-p", "mock"]

    response = MagicMock()
    response.text = text
    response.exit_code = exit_code
    response.stderr = stderr
    response.command = command
    response.working_dir = working_dir
    response.duration = duration
    response.__str__ = lambda self: self.text
    return response
