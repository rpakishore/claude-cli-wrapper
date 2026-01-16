"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def mock_cli_path() -> str:
    """Provide a mock CLI path for testing."""
    return "/usr/local/bin/claude"


@pytest.fixture
def sample_prompt() -> str:
    """Provide a sample prompt for testing."""
    return "Explain Python generators in 2 sentences."
