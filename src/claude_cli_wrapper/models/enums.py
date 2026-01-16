"""Enumerations for claude-cli-wrapper."""

from enum import Enum


class Model(str, Enum):
    """Available Claude models.

    These are aliases that map to the latest version of each model tier.
    You can also pass full model names as strings directly.
    """

    SONNET = "sonnet"
    OPUS = "opus"
    HAIKU = "haiku"

    def __str__(self) -> str:
        """Return the model value for CLI usage."""
        return self.value


class PermissionMode(str, Enum):
    """Permission modes for Claude CLI execution.

    Attributes:
        DEFAULT: Use default permission behavior.
        PLAN: Claude explains actions before executing.
        ACCEPT_EDITS: Automatically accept edit operations.
        BYPASS_PERMISSIONS: Skip all permission checks.
        DONT_ASK: Don't ask for permissions.
        DELEGATE: Delegate permission decisions.
    """

    DEFAULT = "default"
    PLAN = "plan"
    ACCEPT_EDITS = "acceptEdits"
    BYPASS_PERMISSIONS = "bypassPermissions"
    DONT_ASK = "dontAsk"
    DELEGATE = "delegate"

    def __str__(self) -> str:
        """Return the mode value for CLI usage."""
        return self.value


class OutputFormat(str, Enum):
    """Output format options for print mode.

    Attributes:
        TEXT: Plain text output (default).
        JSON: Single JSON result object.
        STREAM_JSON: Streaming JSON messages.
    """

    TEXT = "text"
    JSON = "json"
    STREAM_JSON = "stream-json"

    def __str__(self) -> str:
        """Return the format value for CLI usage."""
        return self.value
