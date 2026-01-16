"""Unit tests for CLI discovery."""

import os
from unittest.mock import patch

import pytest

from claude_cli_wrapper.errors import CLINotFoundError
from claude_cli_wrapper.utils.discovery import resolve_cli_path


class TestResolveCliPath:
    """Tests for resolve_cli_path function."""

    def test_explicit_path_takes_priority(self) -> None:
        """Explicit cli_path should be used directly."""
        result = resolve_cli_path(cli_path="/custom/path/claude")
        assert result == "/custom/path/claude"

    def test_env_variable_used_when_set(self) -> None:
        """CLAUDE_CLI_PATH env var should be used when set."""
        with patch.dict(os.environ, {"CLAUDE_CLI_PATH": "/env/path/claude"}):
            result = resolve_cli_path()
            assert result == "/env/path/claude"

    def test_explicit_path_overrides_env(self) -> None:
        """Explicit path should override environment variable."""
        with patch.dict(os.environ, {"CLAUDE_CLI_PATH": "/env/path/claude"}):
            result = resolve_cli_path(cli_path="/explicit/claude")
            assert result == "/explicit/claude"

    def test_searches_path_when_no_explicit_or_env(self) -> None:
        """Should search PATH when no explicit path or env var."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove CLAUDE_CLI_PATH if it exists
            os.environ.pop("CLAUDE_CLI_PATH", None)
            with patch("shutil.which", return_value="/usr/bin/claude"):
                result = resolve_cli_path()
                assert result == "/usr/bin/claude"

    def test_raises_when_not_found(self) -> None:
        """Should raise CLINotFoundError when CLI cannot be found."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CLAUDE_CLI_PATH", None)
            with patch("shutil.which", return_value=None):
                with pytest.raises(CLINotFoundError) as exc_info:
                    resolve_cli_path()
                assert "not found" in str(exc_info.value).lower()
                assert exc_info.value.cli_path is not None
