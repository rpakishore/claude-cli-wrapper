"""Shared mock responses for tests."""

import json
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


def create_cli_json_envelope(
    result: str = '{"greeting": "hello"}',
    *,
    subtype: str = "success",
    session_id: str = "test-session-123",
    total_cost_usd: float = 0.01,
    num_turns: int = 1,
    duration_ms: int = 1500,
    duration_api_ms: int = 1200,
    is_error: bool = False,
    stop_reason: str = "end_turn",
    structured_output: dict | None = None,
) -> str:
    """Build a realistic CLI JSON envelope string.

    Args:
        result: The ``result`` field (model's text response).
        subtype: Envelope subtype (``"success"``, ``"error_max_turns"``, etc.).
        session_id: Session identifier.
        total_cost_usd: Total cost in USD.
        num_turns: Number of turns.
        duration_ms: Total duration in milliseconds.
        duration_api_ms: API duration in milliseconds.
        is_error: Whether the response is an error.
        stop_reason: Reason the model stopped.
        structured_output: Optional structured output dict.

    Returns:
        A JSON string representing the CLI envelope.
    """
    envelope: dict = {
        "type": "result",
        "subtype": subtype,
        "result": result,
        "session_id": session_id,
        "total_cost_usd": total_cost_usd,
        "usage": {"input_tokens": 100, "output_tokens": 50},
        "num_turns": num_turns,
        "duration_ms": duration_ms,
        "duration_api_ms": duration_api_ms,
        "is_error": is_error,
        "stop_reason": stop_reason,
    }
    if structured_output is not None:
        envelope["structured_output"] = structured_output
    return json.dumps(envelope)
