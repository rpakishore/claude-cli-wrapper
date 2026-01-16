"""Cross-platform utilities."""

from __future__ import annotations

import os
import sys


def is_windows() -> bool:
    """Check if running on Windows.

    Returns:
        True if running on Windows, False otherwise.
    """
    return sys.platform == "win32"


def get_cli_name() -> str:
    """Get the appropriate CLI executable name for the current platform.

    Returns:
        'claude.cmd' on Windows, 'claude' on other platforms.
    """
    return "claude.cmd" if is_windows() else "claude"


def get_env_cli_path() -> str | None:
    """Get CLI path from environment variable if set.

    Returns:
        The path from CLAUDE_CLI_PATH environment variable, or None.
    """
    return os.environ.get("CLAUDE_CLI_PATH")
