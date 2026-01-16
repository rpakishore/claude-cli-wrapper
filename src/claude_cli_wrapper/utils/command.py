"""Command building utilities."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


def build_command(
    cli_path: str,
    *,
    model: str | None = None,
    system_prompt: str | None = None,
    append_system_prompt: str | None = None,
    max_turns: int | None = None,
    output_format: str | None = None,
    json_schema: dict | None = None,
    permission_mode: str | None = None,
    dangerously_skip_permissions: bool = False,
    allowed_tools: list[str] | None = None,
    disallowed_tools: list[str] | None = None,
    tools: list[str] | None = None,
    agents: list[Any] | None = None,
    mcp_config: str | dict | None = None,
    add_dirs: list[str] | None = None,
    files: dict[str, str] | None = None,
    session_id: str | None = None,
    continue_session: bool = False,
    resume: str | None = None,
    fork_session: bool = False,
    fallback_model: str | None = None,
    betas: list[str] | None = None,
    verbose: bool = False,
    no_session_persistence: bool = False,
) -> list[str]:
    """Build the command list for subprocess execution.

    Args:
        cli_path: Path to the Claude CLI executable.
        model: Model to use (e.g., 'opus', 'sonnet', 'haiku').
        system_prompt: Replace the default system prompt.
        append_system_prompt: Append to the default system prompt.
        max_turns: Maximum number of agentic turns.
        output_format: Output format ('text', 'json', 'stream-json').
        json_schema: JSON schema for structured output validation.
        permission_mode: Permission mode for the session.
        dangerously_skip_permissions: Skip all permission checks.
        allowed_tools: List of tools to allow.
        disallowed_tools: List of tools to disallow.
        tools: List of available tools (restricts built-in set).
        agents: List of Agent objects for custom subagents.
        mcp_config: Path to MCP config file or config dict.
        add_dirs: Additional directories to allow tool access to.
        files: Dict of file_id to relative_path for file resources.
        session_id: Specific session ID to use.
        continue_session: Continue the most recent conversation.
        resume: Resume a specific session by ID.
        fork_session: Create a new session ID when resuming.
        fallback_model: Fallback model when primary is overloaded.
        betas: Beta features to enable.
        verbose: Enable verbose output.
        no_session_persistence: Disable session persistence.

    Returns:
        List of command arguments for subprocess.run().
    """
    cmd = [cli_path, "--print"]

    # Model configuration
    if model is not None:
        cmd.extend(["--model", str(model)])

    if fallback_model is not None:
        cmd.extend(["--fallback-model", str(fallback_model)])

    # System prompts
    if system_prompt is not None:
        cmd.extend(["--system-prompt", system_prompt])

    if append_system_prompt is not None:
        cmd.extend(["--append-system-prompt", append_system_prompt])

    # Execution limits
    if max_turns is not None:
        cmd.extend(["--max-turns", str(max_turns)])

    # Output configuration
    if output_format is not None:
        cmd.extend(["--output-format", str(output_format)])

    if json_schema is not None:
        cmd.extend(["--json-schema", json.dumps(json_schema)])

    # Permissions
    if permission_mode is not None:
        cmd.extend(["--permission-mode", str(permission_mode)])

    if dangerously_skip_permissions:
        cmd.append("--dangerously-skip-permissions")

    # Tool configuration
    if allowed_tools is not None:
        cmd.extend(["--allowed-tools", *allowed_tools])

    if disallowed_tools is not None:
        cmd.extend(["--disallowed-tools", *disallowed_tools])

    if tools is not None:
        cmd.extend(["--tools", *tools])

    # Agents
    if agents is not None and len(agents) > 0:
        agents_dict = {agent.name: agent.to_dict() for agent in agents}
        cmd.extend(["--agents", json.dumps(agents_dict)])

    # MCP configuration
    if mcp_config is not None:
        if isinstance(mcp_config, dict):
            cmd.extend(["--mcp-config", json.dumps(mcp_config)])
        else:
            cmd.extend(["--mcp-config", str(mcp_config)])

    # Directories
    if add_dirs is not None:
        cmd.extend(["--add-dir", *[str(d) for d in add_dirs]])

    # Files
    if files is not None:
        file_specs = [f"{file_id}:{path}" for file_id, path in files.items()]
        cmd.extend(["--file", *file_specs])

    # Session management
    if session_id is not None:
        cmd.extend(["--session-id", session_id])

    if continue_session:
        cmd.append("--continue")

    if resume is not None:
        cmd.extend(["--resume", resume])

    if fork_session:
        cmd.append("--fork-session")

    if no_session_persistence:
        cmd.append("--no-session-persistence")

    # Betas
    if betas is not None:
        cmd.extend(["--betas", *betas])

    # Debugging
    if verbose:
        cmd.append("--verbose")

    # The prompt will be provided via stdin, use "-" as placeholder
    cmd.append("-")

    return cmd
