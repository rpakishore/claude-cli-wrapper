"""CLI discovery and path resolution."""

from __future__ import annotations

import shutil

from claude_cli_wrapper.errors import CLINotFoundError
from claude_cli_wrapper.utils.platform import get_cli_name, get_env_cli_path


def resolve_cli_path(cli_path: str | None = None) -> str:
    """Resolve the path to the Claude CLI executable.

    Resolution order:
    1. Explicit cli_path parameter (if provided)
    2. CLAUDE_CLI_PATH environment variable (if set)
    3. 'claude' (or 'claude.cmd' on Windows) in system PATH

    Args:
        cli_path: Explicit path to the CLI executable. If provided,
            this path is used directly without validation.

    Returns:
        The resolved path to the Claude CLI.

    Raises:
        CLINotFoundError: If the CLI cannot be found at any location.

    Example:
        >>> path = resolve_cli_path()
        >>> print(path)  # '/usr/local/bin/claude'
    """
    # 1. Explicit path takes priority
    if cli_path is not None:
        return cli_path

    # 2. Check environment variable
    env_path = get_env_cli_path()
    if env_path is not None:
        return env_path

    # 3. Search in PATH
    cli_name = get_cli_name()
    found_path = shutil.which(cli_name)

    if found_path is not None:
        return found_path

    # Not found - raise with helpful message
    raise CLINotFoundError(
        f"Claude CLI not found. Searched for '{cli_name}' in PATH. "
        f"Install it with: npm install -g @anthropic-ai/claude-code\n"
        f"Or set CLAUDE_CLI_PATH environment variable to the CLI location.",
        cli_path=cli_name,
    )
