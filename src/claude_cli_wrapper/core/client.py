"""Main client functionality for Claude CLI wrapper."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from claude_cli_wrapper.core.response import ClaudeResponse
from claude_cli_wrapper.errors import (
    AuthenticationError,
    CLINotFoundError,
    ExecutionError,
    InvalidArgumentError,
    TimeoutError,
)
from claude_cli_wrapper.utils.command import build_command
from claude_cli_wrapper.utils.discovery import resolve_cli_path

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _extract_from_envelope(raw_stdout: str) -> tuple[str, dict | None]:
    """Extract the model's response from the CLI JSON envelope.

    When ``--output-format json`` is used, the CLI wraps responses in a
    metadata envelope like ``{"type":"result","result":"...","duration_ms":...}``.
    This helper extracts the ``result`` field as the response text and returns
    the full envelope for metadata access.

    Args:
        raw_stdout: The raw stdout from the CLI subprocess.

    Returns:
        A tuple of ``(result_text, envelope_dict)``.  If the stdout is not
        a CLI envelope, returns ``(raw_stdout, None)`` unchanged.
    """
    try:
        data = json.loads(raw_stdout)
    except (json.JSONDecodeError, TypeError):
        return raw_stdout, None

    if isinstance(data, dict) and "type" in data:
        result_text = data.get("result", "")
        if result_text is None:
            result_text = ""
        return str(result_text), data

    return raw_stdout, None


def run(
    prompt: str,
    *,
    # Model configuration
    model: str | None = None,
    fallback_model: str | None = None,
    # System prompts
    system_prompt: str | None = None,
    append_system_prompt: str | None = None,
    # Execution
    working_dir: str | Path | None = None,
    timeout: float | None = None,
    max_turns: int | None = None,
    # Output
    output_format: str | None = None,
    json_schema: dict | None = None,
    response_model: type | None = None,
    # Tools
    allowed_tools: list[str] | None = None,
    disallowed_tools: list[str] | None = None,
    tools: list[str] | None = None,
    # Permissions
    permission_mode: str | None = None,
    dangerously_skip_permissions: bool = True,
    # Session
    session_id: str | None = None,
    continue_session: bool = False,
    resume: str | None = None,
    fork_session: bool = False,
    no_session_persistence: bool = False,
    # Configuration
    cli_path: str | None = None,
    add_dirs: list[str | Path] | None = None,
    mcp_config: str | dict | None = None,
    agents: list[Any] | None = None,
    files: dict[str, str] | None = None,
    betas: list[str] | None = None,
    # Debugging
    verbose: bool = False,
) -> ClaudeResponse:
    """Execute a prompt using the Claude CLI.

    This is the main entry point for interacting with Claude via the CLI.
    The prompt is sent to Claude and the response is returned as a
    ClaudeResponse object.

    Args:
        prompt: The prompt text to send to Claude.
        model: Model to use ('sonnet', 'opus', 'haiku', or full model name).
        fallback_model: Fallback model when primary is overloaded.
        system_prompt: Replace the default system prompt entirely.
        append_system_prompt: Append text to the default system prompt.
        working_dir: Working directory for CLI execution. Defaults to cwd.
        timeout: Timeout in seconds. None means no timeout.
        max_turns: Maximum number of agentic turns.
        output_format: Output format ('text', 'json', 'stream-json').
        json_schema: JSON schema for structured output validation.
        response_model: Pydantic model for parsing the response.
        allowed_tools: List of tools to allow (e.g., ['Read', 'Bash(git:*)']).
        disallowed_tools: List of tools to disallow.
        tools: Restrict available tools to this list.
        permission_mode: Permission mode ('default', 'plan', 'acceptEdits', etc.).
        dangerously_skip_permissions: Skip all permission checks.
        session_id: Use a specific session ID.
        continue_session: Continue the most recent conversation.
        resume: Resume a specific session by ID.
        fork_session: Create new session when resuming.
        no_session_persistence: Disable session persistence.
        cli_path: Path to Claude CLI. Defaults to auto-discovery.
        add_dirs: Additional directories to allow tool access.
        mcp_config: Path to MCP config file or config dict.
        agents: List of Agent objects for custom subagents.
        files: Dict mapping file_id to relative_path.
        betas: List of beta features to enable.
        verbose: Enable verbose CLI output.

    Returns:
        ClaudeResponse containing the result and metadata.

    Raises:
        CLINotFoundError: If the Claude CLI cannot be found.
        AuthenticationError: If not authenticated with the CLI.
        InvalidArgumentError: If invalid arguments are provided.
        TimeoutError: If the operation exceeds the timeout.
        ExecutionError: If the CLI returns a non-zero exit code.

    Example:
        >>> response = run("Explain Python decorators")
        >>> print(response.text)

        >>> response = run(
        ...     "Review this code",
        ...     model="opus",
        ...     system_prompt="Be concise",
        ...     timeout=60,
        ... )
    """
    # Resolve CLI path
    resolved_cli_path = resolve_cli_path(cli_path)
    logger.debug("Using CLI at: %s", resolved_cli_path)

    # Resolve working directory
    if working_dir:
        resolved_working_dir = str(Path(working_dir).resolve())
    else:
        resolved_working_dir = os.getcwd()
    logger.debug("Working directory: %s", resolved_working_dir)

    # Convert Path objects in add_dirs to strings
    resolved_add_dirs = [str(d) for d in add_dirs] if add_dirs else None

    # If response_model is provided, we need JSON output
    effective_output_format = output_format
    effective_json_schema = json_schema
    if response_model is not None:
        effective_output_format = "json"
        if json_schema is None:
            # Generate schema from Pydantic model
            try:
                effective_json_schema = response_model.model_json_schema()
            except AttributeError as e:
                raise InvalidArgumentError(
                    "response_model must be a Pydantic BaseModel class",
                    argument="response_model",
                    value=str(response_model),
                ) from e

    # Auto-set JSON output format when json_schema is provided
    if effective_json_schema is not None and effective_output_format is None:
        effective_output_format = "json"

    # Build command
    command = build_command(
        resolved_cli_path,
        model=str(model) if model else None,
        fallback_model=str(fallback_model) if fallback_model else None,
        system_prompt=system_prompt,
        append_system_prompt=append_system_prompt,
        max_turns=max_turns,
        output_format=effective_output_format,
        json_schema=effective_json_schema,
        permission_mode=str(permission_mode) if permission_mode else None,
        dangerously_skip_permissions=dangerously_skip_permissions,
        allowed_tools=allowed_tools,
        disallowed_tools=disallowed_tools,
        tools=tools,
        agents=agents,
        mcp_config=mcp_config,
        add_dirs=resolved_add_dirs,
        files=files,
        session_id=session_id,
        continue_session=continue_session,
        resume=resume,
        fork_session=fork_session,
        no_session_persistence=no_session_persistence,
        betas=betas,
        verbose=verbose,
    )

    logger.debug("Executing command: %s", command)

    # Execute
    start_time = time.perf_counter()
    try:
        result = subprocess.run(
            command,
            input=prompt,
            capture_output=True,
            text=True,
            cwd=resolved_working_dir,
            timeout=timeout,
        )
    except FileNotFoundError as e:
        raise CLINotFoundError(
            f"Claude CLI not found at '{resolved_cli_path}'. "
            f"Install it with: npm install -g @anthropic-ai/claude-code",
            cli_path=resolved_cli_path,
        ) from e
    except subprocess.TimeoutExpired as e:
        raise TimeoutError(
            f"CLI operation timed out after {timeout} seconds",
            timeout=timeout,
            command=command,
        ) from e

    duration = time.perf_counter() - start_time
    logger.debug(
        "Process completed in %.2fs with exit code %d", duration, result.returncode
    )

    # Check for errors
    if result.returncode != 0:
        stderr_lower = result.stderr.lower() if result.stderr else ""

        # Check for authentication errors
        auth_keywords = ["not logged in", "authenticate", "login"]
        if any(kw in stderr_lower for kw in auth_keywords):
            raise AuthenticationError(
                "Not authenticated with Claude CLI. "
                f"Run 'claude' interactively to log in.\nstderr: {result.stderr}"
            )

        # Check for invalid argument errors
        is_invalid = "invalid" in stderr_lower
        is_arg_or_opt = "argument" in stderr_lower or "option" in stderr_lower
        if is_invalid and is_arg_or_opt:
            raise InvalidArgumentError(
                f"Invalid argument passed to CLI: {result.stderr}",
            )

        # Generic execution error
        raise ExecutionError(
            f"CLI returned exit code {result.returncode}: {result.stderr}",
            exit_code=result.returncode,
            stderr=result.stderr,
            command=command,
        )

    # Extract response from CLI JSON envelope when applicable
    response_text = result.stdout
    cli_envelope = None
    if effective_output_format == "json":
        response_text, cli_envelope = _extract_from_envelope(result.stdout)
        if cli_envelope is not None:
            logger.debug("Extracted response from CLI JSON envelope")

    # Build response
    return ClaudeResponse(
        text=response_text,
        exit_code=result.returncode,
        stderr=result.stderr,
        command=command,
        working_dir=resolved_working_dir,
        duration=duration,
        _json_schema=effective_json_schema,
        _response_model=response_model,
        _cli_envelope=cli_envelope,
    )
