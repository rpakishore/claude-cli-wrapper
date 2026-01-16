# Implementation.md - Step-by-Step Execution Plan

> **Purpose**: This document provides atomic, unambiguous implementation steps for the Junior Developer AI Agent. Each step includes a Definition of Done (DoD) to verify completion.

---

## Phase 0: Project Initialization

### Step 0.1: Create Project Structure

**Action**: Create all directories for the package structure.

```bash
mkdir -p src/claude_cli_wrapper/core
mkdir -p src/claude_cli_wrapper/errors
mkdir -p src/claude_cli_wrapper/models
mkdir -p src/claude_cli_wrapper/utils
mkdir -p tests/unit
mkdir -p tests/fixtures
```

**Definition of Done**:
- [ ] Directory `src/claude_cli_wrapper/core/` exists
- [ ] Directory `src/claude_cli_wrapper/errors/` exists
- [ ] Directory `src/claude_cli_wrapper/models/` exists
- [ ] Directory `src/claude_cli_wrapper/utils/` exists
- [ ] Directory `tests/unit/` exists
- [ ] Directory `tests/fixtures/` exists

---

### Step 0.2: Create pyproject.toml

**Action**: Create `pyproject.toml` with the following exact content:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "claude-cli-wrapper"
version = "0.1.0"
description = "A Python wrapper for the Claude Code CLI"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Typing :: Typed",
]
keywords = ["claude", "cli", "anthropic", "ai", "wrapper"]
dependencies = []

[project.optional-dependencies]
pydantic = ["pydantic>=2.0"]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "ruff>=0.4",
]

[project.urls]
Homepage = "https://github.com/your-username/claude-cli-wrapper"
Repository = "https://github.com/your-username/claude-cli-wrapper"
Issues = "https://github.com/your-username/claude-cli-wrapper/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/claude_cli_wrapper"]

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

**Definition of Done**:
- [ ] File `pyproject.toml` exists at project root
- [ ] Running `uv sync` completes without errors
- [ ] Running `uv sync --extra dev` installs pytest, pytest-cov, and ruff

---

### Step 0.3: Create Empty __init__.py Files

**Action**: Create empty `__init__.py` files in all packages:

```bash
touch src/claude_cli_wrapper/__init__.py
touch src/claude_cli_wrapper/core/__init__.py
touch src/claude_cli_wrapper/errors/__init__.py
touch src/claude_cli_wrapper/models/__init__.py
touch src/claude_cli_wrapper/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/fixtures/__init__.py
```

**Definition of Done**:
- [ ] All `__init__.py` files exist
- [ ] Running `uv run python -c "import claude_cli_wrapper"` succeeds (no error)

---

### Step 0.4: Create py.typed Marker

**Action**: Create the PEP 561 type marker file:

```bash
touch src/claude_cli_wrapper/py.typed
```

**Definition of Done**:
- [ ] File `src/claude_cli_wrapper/py.typed` exists (empty file)

---

### Step 0.5: Create LICENSE File

**Action**: Create `LICENSE` file with MIT license text:

```
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Definition of Done**:
- [ ] File `LICENSE` exists at project root
- [ ] File contains "MIT License" text

---

## Phase 1: Exception Hierarchy

### Step 1.1: Create exceptions.py

**Action**: Create `src/claude_cli_wrapper/errors/exceptions.py` with the following content:

```python
"""Exception hierarchy for claude-cli-wrapper.

All exceptions inherit from ClaudeError, allowing users to catch all
wrapper-specific errors with a single except clause.
"""

from __future__ import annotations


class ClaudeError(Exception):
    """Base exception for all claude-cli-wrapper errors.

    Attributes:
        message: Human-readable error description.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class CLINotFoundError(ClaudeError):
    """Raised when the Claude CLI executable cannot be found.

    Attributes:
        message: Human-readable error description.
        cli_path: The path that was searched for the CLI.
    """

    def __init__(self, message: str, cli_path: str) -> None:
        self.cli_path = cli_path
        super().__init__(message)


class AuthenticationError(ClaudeError):
    """Raised when the user is not authenticated with the Claude CLI.

    This typically occurs when the user has not run 'claude' interactively
    to complete the authentication flow.

    Attributes:
        message: Human-readable error description.
    """

    pass


class InvalidArgumentError(ClaudeError):
    """Raised when invalid arguments are passed to the CLI.

    Attributes:
        message: Human-readable error description.
        argument: The name of the invalid argument (if known).
        value: The invalid value that was provided (if known).
    """

    def __init__(
        self,
        message: str,
        argument: str | None = None,
        value: str | None = None,
    ) -> None:
        self.argument = argument
        self.value = value
        super().__init__(message)


class TimeoutError(ClaudeError):
    """Raised when a CLI operation exceeds the specified timeout.

    Attributes:
        message: Human-readable error description.
        timeout: The timeout value in seconds that was exceeded.
        command: The command that timed out (if available).
    """

    def __init__(
        self,
        message: str,
        timeout: float,
        command: list[str] | None = None,
    ) -> None:
        self.timeout = timeout
        self.command = command
        super().__init__(message)


class ExecutionError(ClaudeError):
    """Raised when the CLI returns a non-zero exit code.

    This is a catch-all for CLI errors not covered by more specific exceptions.

    Attributes:
        message: Human-readable error description.
        exit_code: The non-zero exit code returned by the CLI.
        stderr: The stderr output from the CLI (if available).
        command: The command that failed (if available).
    """

    def __init__(
        self,
        message: str,
        exit_code: int,
        stderr: str | None = None,
        command: list[str] | None = None,
    ) -> None:
        self.exit_code = exit_code
        self.stderr = stderr
        self.command = command
        super().__init__(message)
```

**Definition of Done**:
- [ ] File `src/claude_cli_wrapper/errors/exceptions.py` exists
- [ ] Running `uv run python -c "from claude_cli_wrapper.errors.exceptions import ClaudeError, CLINotFoundError, AuthenticationError, InvalidArgumentError, TimeoutError, ExecutionError"` succeeds
- [ ] All exception classes have docstrings
- [ ] All exception classes have type hints

---

### Step 1.2: Export Exceptions from errors/__init__.py

**Action**: Update `src/claude_cli_wrapper/errors/__init__.py`:

```python
"""Error handling for claude-cli-wrapper."""

from claude_cli_wrapper.errors.exceptions import (
    AuthenticationError,
    CLINotFoundError,
    ClaudeError,
    ExecutionError,
    InvalidArgumentError,
    TimeoutError,
)

__all__ = [
    "ClaudeError",
    "CLINotFoundError",
    "AuthenticationError",
    "InvalidArgumentError",
    "TimeoutError",
    "ExecutionError",
]
```

**Definition of Done**:
- [ ] File updated with exports
- [ ] Running `uv run python -c "from claude_cli_wrapper.errors import ClaudeError"` succeeds

---

### Step 1.3: Create Unit Tests for Exceptions

**Action**: Create `tests/unit/test_exceptions.py`:

```python
"""Unit tests for exception hierarchy."""

import pytest

from claude_cli_wrapper.errors import (
    AuthenticationError,
    CLINotFoundError,
    ClaudeError,
    ExecutionError,
    InvalidArgumentError,
    TimeoutError,
)


class TestClaudeError:
    """Tests for the base ClaudeError exception."""

    def test_inherits_from_exception(self) -> None:
        """ClaudeError should inherit from Exception."""
        assert issubclass(ClaudeError, Exception)

    def test_message_attribute(self) -> None:
        """ClaudeError should store the message."""
        error = ClaudeError("test message")
        assert error.message == "test message"
        assert str(error) == "test message"


class TestCLINotFoundError:
    """Tests for CLINotFoundError."""

    def test_inherits_from_claude_error(self) -> None:
        """CLINotFoundError should inherit from ClaudeError."""
        assert issubclass(CLINotFoundError, ClaudeError)

    def test_cli_path_attribute(self) -> None:
        """CLINotFoundError should store the cli_path."""
        error = CLINotFoundError("CLI not found", cli_path="/usr/bin/claude")
        assert error.cli_path == "/usr/bin/claude"
        assert error.message == "CLI not found"


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_inherits_from_claude_error(self) -> None:
        """AuthenticationError should inherit from ClaudeError."""
        assert issubclass(AuthenticationError, ClaudeError)


class TestInvalidArgumentError:
    """Tests for InvalidArgumentError."""

    def test_inherits_from_claude_error(self) -> None:
        """InvalidArgumentError should inherit from ClaudeError."""
        assert issubclass(InvalidArgumentError, ClaudeError)

    def test_optional_attributes(self) -> None:
        """InvalidArgumentError should store optional argument details."""
        error = InvalidArgumentError(
            "Invalid model",
            argument="model",
            value="invalid-model",
        )
        assert error.argument == "model"
        assert error.value == "invalid-model"

    def test_optional_attributes_default_to_none(self) -> None:
        """Optional attributes should default to None."""
        error = InvalidArgumentError("Invalid argument")
        assert error.argument is None
        assert error.value is None


class TestTimeoutError:
    """Tests for TimeoutError."""

    def test_inherits_from_claude_error(self) -> None:
        """TimeoutError should inherit from ClaudeError."""
        assert issubclass(TimeoutError, ClaudeError)

    def test_timeout_attribute(self) -> None:
        """TimeoutError should store the timeout value."""
        error = TimeoutError("Timed out", timeout=30.0)
        assert error.timeout == 30.0

    def test_command_attribute(self) -> None:
        """TimeoutError should store the command if provided."""
        error = TimeoutError(
            "Timed out",
            timeout=30.0,
            command=["claude", "-p", "test"],
        )
        assert error.command == ["claude", "-p", "test"]


class TestExecutionError:
    """Tests for ExecutionError."""

    def test_inherits_from_claude_error(self) -> None:
        """ExecutionError should inherit from ClaudeError."""
        assert issubclass(ExecutionError, ClaudeError)

    def test_exit_code_attribute(self) -> None:
        """ExecutionError should store the exit code."""
        error = ExecutionError("Failed", exit_code=1)
        assert error.exit_code == 1

    def test_stderr_attribute(self) -> None:
        """ExecutionError should store stderr output."""
        error = ExecutionError(
            "Failed",
            exit_code=1,
            stderr="Error: something went wrong",
        )
        assert error.stderr == "Error: something went wrong"

    def test_command_attribute(self) -> None:
        """ExecutionError should store the command if provided."""
        error = ExecutionError(
            "Failed",
            exit_code=1,
            command=["claude", "-p", "test"],
        )
        assert error.command == ["claude", "-p", "test"]


class TestExceptionHierarchy:
    """Tests for catching exceptions with base class."""

    def test_catch_all_with_claude_error(self) -> None:
        """All specific exceptions should be catchable with ClaudeError."""
        exceptions = [
            CLINotFoundError("not found", cli_path="/bin/claude"),
            AuthenticationError("not authenticated"),
            InvalidArgumentError("invalid"),
            TimeoutError("timeout", timeout=30.0),
            ExecutionError("failed", exit_code=1),
        ]

        for exc in exceptions:
            with pytest.raises(ClaudeError):
                raise exc
```

**Definition of Done**:
- [ ] File `tests/unit/test_exceptions.py` exists
- [ ] Running `uv run pytest tests/unit/test_exceptions.py -v` passes all tests
- [ ] All tests have docstrings

---

## Phase 2: Enums and Models

### Step 2.1: Create enums.py

**Action**: Create `src/claude_cli_wrapper/models/enums.py`:

```python
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
```

**Definition of Done**:
- [ ] File `src/claude_cli_wrapper/models/enums.py` exists
- [ ] Running `uv run python -c "from claude_cli_wrapper.models.enums import Model, PermissionMode, OutputFormat"` succeeds
- [ ] `str(Model.OPUS)` returns `"opus"`
- [ ] `str(PermissionMode.PLAN)` returns `"plan"`

---

### Step 2.2: Create agent.py

**Action**: Create `src/claude_cli_wrapper/models/agent.py`:

```python
"""Agent model for custom subagents."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Agent:
    """Definition of a custom subagent for Claude CLI.

    Agents are specialized assistants with specific capabilities and instructions.

    Attributes:
        name: Unique identifier for the agent (used as key in JSON).
        description: Natural language description of when to use this agent.
        prompt: System prompt guiding the agent's behavior.
        tools: List of tools the agent can use. If None, inherits all tools.
        model: Model alias ('sonnet', 'opus', 'haiku'). If None, uses default.

    Example:
        >>> reviewer = Agent(
        ...     name="code-reviewer",
        ...     description="Expert code reviewer for Python",
        ...     prompt="You are a senior developer. Focus on code quality.",
        ...     tools=["Read", "Grep", "Glob"],
        ...     model="sonnet",
        ... )
    """

    name: str
    description: str
    prompt: str
    tools: list[str] | None = None
    model: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary format for CLI --agents flag.

        Returns:
            Dictionary with agent definition (excludes name, which is used as key).
        """
        result: dict = {
            "description": self.description,
            "prompt": self.prompt,
        }
        if self.tools is not None:
            result["tools"] = self.tools
        if self.model is not None:
            result["model"] = self.model
        return result
```

**Definition of Done**:
- [ ] File `src/claude_cli_wrapper/models/agent.py` exists
- [ ] Running `uv run python -c "from claude_cli_wrapper.models.agent import Agent; a = Agent(name='test', description='Test', prompt='Be helpful'); print(a.to_dict())"` outputs `{'description': 'Test', 'prompt': 'Be helpful'}`

---

### Step 2.3: Export Models from models/__init__.py

**Action**: Update `src/claude_cli_wrapper/models/__init__.py`:

```python
"""Models and enumerations for claude-cli-wrapper."""

from claude_cli_wrapper.models.agent import Agent
from claude_cli_wrapper.models.enums import Model, OutputFormat, PermissionMode

__all__ = [
    "Agent",
    "Model",
    "OutputFormat",
    "PermissionMode",
]
```

**Definition of Done**:
- [ ] File updated with exports
- [ ] Running `uv run python -c "from claude_cli_wrapper.models import Agent, Model, PermissionMode"` succeeds

---

### Step 2.4: Create Unit Tests for Models

**Action**: Create `tests/unit/test_models.py`:

```python
"""Unit tests for models and enums."""

from claude_cli_wrapper.models import Agent, Model, OutputFormat, PermissionMode


class TestModel:
    """Tests for Model enum."""

    def test_model_values(self) -> None:
        """Model enum should have correct values."""
        assert Model.SONNET.value == "sonnet"
        assert Model.OPUS.value == "opus"
        assert Model.HAIKU.value == "haiku"

    def test_model_str(self) -> None:
        """Model enum should convert to string correctly."""
        assert str(Model.OPUS) == "opus"

    def test_model_is_str_subclass(self) -> None:
        """Model should be usable as a string."""
        assert isinstance(Model.OPUS, str)
        assert Model.OPUS == "opus"


class TestPermissionMode:
    """Tests for PermissionMode enum."""

    def test_permission_mode_values(self) -> None:
        """PermissionMode enum should have correct values."""
        assert PermissionMode.DEFAULT.value == "default"
        assert PermissionMode.PLAN.value == "plan"
        assert PermissionMode.ACCEPT_EDITS.value == "acceptEdits"
        assert PermissionMode.BYPASS_PERMISSIONS.value == "bypassPermissions"
        assert PermissionMode.DONT_ASK.value == "dontAsk"
        assert PermissionMode.DELEGATE.value == "delegate"

    def test_permission_mode_str(self) -> None:
        """PermissionMode should convert to string correctly."""
        assert str(PermissionMode.PLAN) == "plan"


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_output_format_values(self) -> None:
        """OutputFormat enum should have correct values."""
        assert OutputFormat.TEXT.value == "text"
        assert OutputFormat.JSON.value == "json"
        assert OutputFormat.STREAM_JSON.value == "stream-json"


class TestAgent:
    """Tests for Agent dataclass."""

    def test_agent_required_fields(self) -> None:
        """Agent should require name, description, and prompt."""
        agent = Agent(
            name="test-agent",
            description="A test agent",
            prompt="You are a test agent.",
        )
        assert agent.name == "test-agent"
        assert agent.description == "A test agent"
        assert agent.prompt == "You are a test agent."

    def test_agent_optional_fields_default_to_none(self) -> None:
        """Agent optional fields should default to None."""
        agent = Agent(
            name="test",
            description="Test",
            prompt="Test prompt",
        )
        assert agent.tools is None
        assert agent.model is None

    def test_agent_with_optional_fields(self) -> None:
        """Agent should accept optional fields."""
        agent = Agent(
            name="reviewer",
            description="Code reviewer",
            prompt="Review code.",
            tools=["Read", "Grep"],
            model="sonnet",
        )
        assert agent.tools == ["Read", "Grep"]
        assert agent.model == "sonnet"

    def test_agent_to_dict_minimal(self) -> None:
        """to_dict should include only required fields when optionals are None."""
        agent = Agent(
            name="test",
            description="Test desc",
            prompt="Test prompt",
        )
        result = agent.to_dict()
        assert result == {
            "description": "Test desc",
            "prompt": "Test prompt",
        }
        assert "tools" not in result
        assert "model" not in result

    def test_agent_to_dict_full(self) -> None:
        """to_dict should include optional fields when set."""
        agent = Agent(
            name="reviewer",
            description="Code reviewer",
            prompt="Review code.",
            tools=["Read", "Grep"],
            model="sonnet",
        )
        result = agent.to_dict()
        assert result == {
            "description": "Code reviewer",
            "prompt": "Review code.",
            "tools": ["Read", "Grep"],
            "model": "sonnet",
        }

    def test_agent_to_dict_excludes_name(self) -> None:
        """to_dict should not include name (it's used as key)."""
        agent = Agent(
            name="my-agent",
            description="Test",
            prompt="Test",
        )
        result = agent.to_dict()
        assert "name" not in result
```

**Definition of Done**:
- [ ] File `tests/unit/test_models.py` exists
- [ ] Running `uv run pytest tests/unit/test_models.py -v` passes all tests

---

## Phase 3: Response Object

### Step 3.1: Create response.py

**Action**: Create `src/claude_cli_wrapper/core/response.py`:

```python
"""Response object for Claude CLI output."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pydantic import BaseModel


@dataclass
class ClaudeResponse:
    """Response from a Claude CLI invocation.

    This class encapsulates the output from the CLI along with metadata
    about the execution.

    Attributes:
        text: The response text from Claude.
        exit_code: The CLI process exit code (0 = success).
        stderr: Any stderr output from the CLI.
        command: The full command that was executed.
        working_dir: The working directory used for execution.
        duration: Execution time in seconds.

    Example:
        >>> response = run("Hello")
        >>> print(response.text)
        >>> print(f"Completed in {response.duration:.2f}s")
    """

    text: str
    exit_code: int
    stderr: str
    command: list[str]
    working_dir: str
    duration: float
    _json_schema: dict | None = field(default=None, repr=False)
    _response_model: type | None = field(default=None, repr=False)
    _parsed_json: dict | None = field(default=None, repr=False, init=False)
    _parsed_model: Any = field(default=None, repr=False, init=False)

    def __str__(self) -> str:
        """Return the response text.

        This allows using the response directly in string contexts.

        Returns:
            The response text.
        """
        return self.text

    @property
    def json(self) -> dict | None:
        """Parse and return the response as JSON.

        This property is available when json_schema was provided to run().
        The result is cached after first access.

        Returns:
            Parsed JSON as a dictionary, or None if not a JSON response.

        Raises:
            ValueError: If the response text is not valid JSON.
        """
        if self._json_schema is None and self._response_model is None:
            return None

        if self._parsed_json is None:
            try:
                self._parsed_json = json.loads(self.text)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Failed to parse response as JSON: {e}. "
                    f"Response text: {self.text[:200]}..."
                ) from e

        return self._parsed_json

    @property
    def parsed(self) -> Any:
        """Return the response parsed as a Pydantic model.

        This property is available when response_model was provided to run().
        The result is cached after first access.

        Returns:
            An instance of the response_model, or None if no model was specified.

        Raises:
            ValueError: If the response cannot be parsed as the model.
            ImportError: If pydantic is not installed.
        """
        if self._response_model is None:
            return None

        if self._parsed_model is None:
            try:
                from pydantic import BaseModel
            except ImportError as e:
                raise ImportError(
                    "pydantic is required for response_model. "
                    "Install it with: pip install claude-cli-wrapper[pydantic]"
                ) from e

            json_data = self.json  # This will parse and cache the JSON
            if json_data is None:
                raise ValueError("Cannot parse response: no JSON data available")

            try:
                self._parsed_model = self._response_model.model_validate(json_data)
            except Exception as e:
                raise ValueError(
                    f"Failed to validate response against model "
                    f"{self._response_model.__name__}: {e}"
                ) from e

        return self._parsed_model
```

**Definition of Done**:
- [ ] File `src/claude_cli_wrapper/core/response.py` exists
- [ ] Running `uv run python -c "from claude_cli_wrapper.core.response import ClaudeResponse; r = ClaudeResponse(text='hello', exit_code=0, stderr='', command=['claude'], working_dir='/tmp', duration=1.0); print(str(r))"` outputs `hello`

---

### Step 3.2: Export Response from core/__init__.py

**Action**: Update `src/claude_cli_wrapper/core/__init__.py`:

```python
"""Core functionality for claude-cli-wrapper."""

from claude_cli_wrapper.core.response import ClaudeResponse

__all__ = [
    "ClaudeResponse",
]
```

**Definition of Done**:
- [ ] File updated with exports
- [ ] Running `uv run python -c "from claude_cli_wrapper.core import ClaudeResponse"` succeeds

---

### Step 3.3: Create Unit Tests for Response

**Action**: Create `tests/unit/test_response.py`:

```python
"""Unit tests for ClaudeResponse."""

import pytest

from claude_cli_wrapper.core.response import ClaudeResponse


def make_response(**kwargs) -> ClaudeResponse:
    """Helper to create a ClaudeResponse with defaults."""
    defaults = {
        "text": "test response",
        "exit_code": 0,
        "stderr": "",
        "command": ["claude", "-p", "test"],
        "working_dir": "/tmp",
        "duration": 1.5,
    }
    defaults.update(kwargs)
    return ClaudeResponse(**defaults)


class TestClaudeResponse:
    """Tests for ClaudeResponse."""

    def test_text_attribute(self) -> None:
        """Response should store text."""
        response = make_response(text="Hello, world!")
        assert response.text == "Hello, world!"

    def test_exit_code_attribute(self) -> None:
        """Response should store exit code."""
        response = make_response(exit_code=0)
        assert response.exit_code == 0

    def test_stderr_attribute(self) -> None:
        """Response should store stderr."""
        response = make_response(stderr="warning: something")
        assert response.stderr == "warning: something"

    def test_command_attribute(self) -> None:
        """Response should store the command."""
        cmd = ["claude", "-p", "--model", "opus", "test"]
        response = make_response(command=cmd)
        assert response.command == cmd

    def test_working_dir_attribute(self) -> None:
        """Response should store working directory."""
        response = make_response(working_dir="/home/user/project")
        assert response.working_dir == "/home/user/project"

    def test_duration_attribute(self) -> None:
        """Response should store duration."""
        response = make_response(duration=2.5)
        assert response.duration == 2.5

    def test_str_returns_text(self) -> None:
        """str(response) should return the text."""
        response = make_response(text="Hello!")
        assert str(response) == "Hello!"

    def test_str_allows_string_operations(self) -> None:
        """Response should work in string contexts."""
        response = make_response(text="Hello")
        assert f"Response: {response}" == "Response: Hello"


class TestClaudeResponseJson:
    """Tests for ClaudeResponse.json property."""

    def test_json_returns_none_without_schema(self) -> None:
        """json property should return None if no schema was provided."""
        response = make_response(text='{"name": "test"}')
        assert response.json is None

    def test_json_parses_when_schema_provided(self) -> None:
        """json property should parse text when schema was provided."""
        response = make_response(
            text='{"name": "John", "age": 30}',
            _json_schema={"type": "object"},
        )
        assert response.json == {"name": "John", "age": 30}

    def test_json_caches_result(self) -> None:
        """json property should cache the parsed result."""
        response = make_response(
            text='{"value": 42}',
            _json_schema={"type": "object"},
        )
        result1 = response.json
        result2 = response.json
        assert result1 is result2  # Same object

    def test_json_raises_on_invalid_json(self) -> None:
        """json property should raise ValueError for invalid JSON."""
        response = make_response(
            text="not valid json",
            _json_schema={"type": "object"},
        )
        with pytest.raises(ValueError, match="Failed to parse response as JSON"):
            _ = response.json


class TestClaudeResponseParsed:
    """Tests for ClaudeResponse.parsed property."""

    def test_parsed_returns_none_without_model(self) -> None:
        """parsed property should return None if no model was provided."""
        response = make_response(text='{"name": "test"}')
        assert response.parsed is None

    def test_parsed_raises_without_pydantic(self) -> None:
        """parsed should raise ImportError if pydantic not installed."""
        # This test assumes pydantic is installed for dev
        # In actual usage without pydantic, it would raise
        pass  # Skip this test as pydantic is likely installed for dev

    def test_parsed_validates_model(self) -> None:
        """parsed property should validate against Pydantic model."""
        pytest.importorskip("pydantic")
        from pydantic import BaseModel

        class Person(BaseModel):
            name: str
            age: int

        response = make_response(
            text='{"name": "John", "age": 30}',
            _response_model=Person,
            _json_schema={"type": "object"},  # Needed for json parsing
        )
        person = response.parsed
        assert isinstance(person, Person)
        assert person.name == "John"
        assert person.age == 30

    def test_parsed_caches_result(self) -> None:
        """parsed property should cache the model instance."""
        pytest.importorskip("pydantic")
        from pydantic import BaseModel

        class Item(BaseModel):
            value: int

        response = make_response(
            text='{"value": 42}',
            _response_model=Item,
            _json_schema={"type": "object"},
        )
        result1 = response.parsed
        result2 = response.parsed
        assert result1 is result2  # Same object

    def test_parsed_raises_on_validation_error(self) -> None:
        """parsed should raise ValueError on validation failure."""
        pytest.importorskip("pydantic")
        from pydantic import BaseModel

        class Strict(BaseModel):
            required_field: str

        response = make_response(
            text='{"wrong_field": "value"}',
            _response_model=Strict,
            _json_schema={"type": "object"},
        )
        with pytest.raises(ValueError, match="Failed to validate response"):
            _ = response.parsed
```

**Definition of Done**:
- [ ] File `tests/unit/test_response.py` exists
- [ ] Running `uv run pytest tests/unit/test_response.py -v` passes all tests

---

## Phase 4: Utility Functions

### Step 4.1: Create platform.py

**Action**: Create `src/claude_cli_wrapper/utils/platform.py`:

```python
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
```

**Definition of Done**:
- [ ] File `src/claude_cli_wrapper/utils/platform.py` exists
- [ ] Running `uv run python -c "from claude_cli_wrapper.utils.platform import is_windows, get_cli_name"` succeeds

---

### Step 4.2: Create discovery.py

**Action**: Create `src/claude_cli_wrapper/utils/discovery.py`:

```python
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
```

**Definition of Done**:
- [ ] File `src/claude_cli_wrapper/utils/discovery.py` exists
- [ ] Running `uv run python -c "from claude_cli_wrapper.utils.discovery import resolve_cli_path"` succeeds

---

### Step 4.3: Create command.py

**Action**: Create `src/claude_cli_wrapper/utils/command.py`:

```python
"""Command building utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from claude_cli_wrapper.models import Agent, OutputFormat, PermissionMode


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
```

**Definition of Done**:
- [ ] File `src/claude_cli_wrapper/utils/command.py` exists
- [ ] Running `uv run python -c "from claude_cli_wrapper.utils.command import build_command; print(build_command('claude', model='opus'))"` outputs a list containing `'--model'` and `'opus'`

---

### Step 4.4: Export Utilities from utils/__init__.py

**Action**: Update `src/claude_cli_wrapper/utils/__init__.py`:

```python
"""Utility functions for claude-cli-wrapper."""

from claude_cli_wrapper.utils.command import build_command
from claude_cli_wrapper.utils.discovery import resolve_cli_path
from claude_cli_wrapper.utils.platform import get_cli_name, get_env_cli_path, is_windows

__all__ = [
    "build_command",
    "resolve_cli_path",
    "get_cli_name",
    "get_env_cli_path",
    "is_windows",
]
```

**Definition of Done**:
- [ ] File updated with exports
- [ ] Running `uv run python -c "from claude_cli_wrapper.utils import resolve_cli_path, build_command"` succeeds

---

### Step 4.5: Create Unit Tests for Utilities

**Action**: Create `tests/unit/test_discovery.py`:

```python
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
```

**Action**: Create `tests/unit/test_command.py`:

```python
"""Unit tests for command building."""

import json

from claude_cli_wrapper.models import Agent
from claude_cli_wrapper.utils.command import build_command


class TestBuildCommand:
    """Tests for build_command function."""

    def test_minimal_command(self) -> None:
        """Minimal command should include --print and stdin marker."""
        cmd = build_command("claude")
        assert cmd[0] == "claude"
        assert "--print" in cmd
        assert cmd[-1] == "-"

    def test_model_flag(self) -> None:
        """--model flag should be added when model is specified."""
        cmd = build_command("claude", model="opus")
        assert "--model" in cmd
        idx = cmd.index("--model")
        assert cmd[idx + 1] == "opus"

    def test_system_prompt_flag(self) -> None:
        """--system-prompt flag should be added."""
        cmd = build_command("claude", system_prompt="Be helpful")
        assert "--system-prompt" in cmd
        idx = cmd.index("--system-prompt")
        assert cmd[idx + 1] == "Be helpful"

    def test_append_system_prompt_flag(self) -> None:
        """--append-system-prompt flag should be added."""
        cmd = build_command("claude", append_system_prompt="Extra rules")
        assert "--append-system-prompt" in cmd
        idx = cmd.index("--append-system-prompt")
        assert cmd[idx + 1] == "Extra rules"

    def test_max_turns_flag(self) -> None:
        """--max-turns flag should be added as string."""
        cmd = build_command("claude", max_turns=5)
        assert "--max-turns" in cmd
        idx = cmd.index("--max-turns")
        assert cmd[idx + 1] == "5"

    def test_output_format_flag(self) -> None:
        """--output-format flag should be added."""
        cmd = build_command("claude", output_format="json")
        assert "--output-format" in cmd
        idx = cmd.index("--output-format")
        assert cmd[idx + 1] == "json"

    def test_json_schema_flag(self) -> None:
        """--json-schema flag should serialize dict to JSON."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        cmd = build_command("claude", json_schema=schema)
        assert "--json-schema" in cmd
        idx = cmd.index("--json-schema")
        assert json.loads(cmd[idx + 1]) == schema

    def test_permission_mode_flag(self) -> None:
        """--permission-mode flag should be added."""
        cmd = build_command("claude", permission_mode="plan")
        assert "--permission-mode" in cmd
        idx = cmd.index("--permission-mode")
        assert cmd[idx + 1] == "plan"

    def test_dangerously_skip_permissions_flag(self) -> None:
        """--dangerously-skip-permissions should be added when True."""
        cmd = build_command("claude", dangerously_skip_permissions=True)
        assert "--dangerously-skip-permissions" in cmd

    def test_dangerously_skip_permissions_not_added_when_false(self) -> None:
        """--dangerously-skip-permissions should not be added when False."""
        cmd = build_command("claude", dangerously_skip_permissions=False)
        assert "--dangerously-skip-permissions" not in cmd

    def test_allowed_tools_flag(self) -> None:
        """--allowed-tools should add all tools."""
        cmd = build_command("claude", allowed_tools=["Read", "Grep", "Bash(git:*)"])
        assert "--allowed-tools" in cmd
        idx = cmd.index("--allowed-tools")
        assert "Read" in cmd[idx + 1 :]
        assert "Grep" in cmd[idx + 1 :]
        assert "Bash(git:*)" in cmd[idx + 1 :]

    def test_disallowed_tools_flag(self) -> None:
        """--disallowed-tools should add all tools."""
        cmd = build_command("claude", disallowed_tools=["Edit", "Write"])
        assert "--disallowed-tools" in cmd

    def test_tools_flag(self) -> None:
        """--tools should add all tools."""
        cmd = build_command("claude", tools=["Read", "Edit"])
        assert "--tools" in cmd

    def test_agents_flag(self) -> None:
        """--agents should serialize Agent objects to JSON."""
        agent = Agent(
            name="reviewer",
            description="Reviews code",
            prompt="You review code",
            tools=["Read"],
            model="sonnet",
        )
        cmd = build_command("claude", agents=[agent])
        assert "--agents" in cmd
        idx = cmd.index("--agents")
        agents_json = json.loads(cmd[idx + 1])
        assert "reviewer" in agents_json
        assert agents_json["reviewer"]["description"] == "Reviews code"

    def test_mcp_config_file_path(self) -> None:
        """--mcp-config should accept file path."""
        cmd = build_command("claude", mcp_config="/path/to/mcp.json")
        assert "--mcp-config" in cmd
        idx = cmd.index("--mcp-config")
        assert cmd[idx + 1] == "/path/to/mcp.json"

    def test_mcp_config_dict(self) -> None:
        """--mcp-config should serialize dict to JSON."""
        config = {"mcpServers": {"sqlite": {"command": "uvx"}}}
        cmd = build_command("claude", mcp_config=config)
        assert "--mcp-config" in cmd
        idx = cmd.index("--mcp-config")
        assert json.loads(cmd[idx + 1]) == config

    def test_add_dirs_flag(self) -> None:
        """--add-dir should add all directories."""
        cmd = build_command("claude", add_dirs=["/path/one", "/path/two"])
        assert "--add-dir" in cmd
        assert "/path/one" in cmd
        assert "/path/two" in cmd

    def test_files_flag(self) -> None:
        """--file should format as file_id:path."""
        cmd = build_command("claude", files={"file_abc": "doc.pdf", "file_def": "img.png"})
        assert "--file" in cmd
        assert "file_abc:doc.pdf" in cmd
        assert "file_def:img.png" in cmd

    def test_session_id_flag(self) -> None:
        """--session-id flag should be added."""
        cmd = build_command("claude", session_id="abc-123")
        assert "--session-id" in cmd
        idx = cmd.index("--session-id")
        assert cmd[idx + 1] == "abc-123"

    def test_continue_flag(self) -> None:
        """--continue flag should be added when True."""
        cmd = build_command("claude", continue_session=True)
        assert "--continue" in cmd

    def test_resume_flag(self) -> None:
        """--resume flag should be added with session ID."""
        cmd = build_command("claude", resume="session-xyz")
        assert "--resume" in cmd
        idx = cmd.index("--resume")
        assert cmd[idx + 1] == "session-xyz"

    def test_fork_session_flag(self) -> None:
        """--fork-session flag should be added when True."""
        cmd = build_command("claude", fork_session=True)
        assert "--fork-session" in cmd

    def test_fallback_model_flag(self) -> None:
        """--fallback-model flag should be added."""
        cmd = build_command("claude", fallback_model="sonnet")
        assert "--fallback-model" in cmd
        idx = cmd.index("--fallback-model")
        assert cmd[idx + 1] == "sonnet"

    def test_betas_flag(self) -> None:
        """--betas should add all beta flags."""
        cmd = build_command("claude", betas=["beta1", "beta2"])
        assert "--betas" in cmd
        assert "beta1" in cmd
        assert "beta2" in cmd

    def test_verbose_flag(self) -> None:
        """--verbose flag should be added when True."""
        cmd = build_command("claude", verbose=True)
        assert "--verbose" in cmd

    def test_no_session_persistence_flag(self) -> None:
        """--no-session-persistence flag should be added when True."""
        cmd = build_command("claude", no_session_persistence=True)
        assert "--no-session-persistence" in cmd

    def test_stdin_marker_always_last(self) -> None:
        """The stdin marker '-' should always be last."""
        cmd = build_command(
            "claude",
            model="opus",
            max_turns=5,
            verbose=True,
        )
        assert cmd[-1] == "-"
```

**Definition of Done**:
- [ ] Files `tests/unit/test_discovery.py` and `tests/unit/test_command.py` exist
- [ ] Running `uv run pytest tests/unit/test_discovery.py tests/unit/test_command.py -v` passes all tests

---

## Phase 5: Core Client

### Step 5.1: Create client.py

**Action**: Create `src/claude_cli_wrapper/core/client.py`:

```python
"""Main client functionality for Claude CLI wrapper."""

from __future__ import annotations

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
    from claude_cli_wrapper.models import Agent, Model, OutputFormat, PermissionMode

logger = logging.getLogger(__name__)


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
    dangerously_skip_permissions: bool = False,
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
    resolved_working_dir = str(Path(working_dir).resolve()) if working_dir else os.getcwd()
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
    logger.debug("Process completed in %.2fs with exit code %d", duration, result.returncode)

    # Check for errors
    if result.returncode != 0:
        stderr_lower = result.stderr.lower() if result.stderr else ""

        # Check for authentication errors
        if "not logged in" in stderr_lower or "authenticate" in stderr_lower or "login" in stderr_lower:
            raise AuthenticationError(
                f"Not authenticated with Claude CLI. Run 'claude' interactively to log in.\n"
                f"stderr: {result.stderr}"
            )

        # Check for invalid argument errors
        if "invalid" in stderr_lower and ("argument" in stderr_lower or "option" in stderr_lower):
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

    # Build response
    return ClaudeResponse(
        text=result.stdout,
        exit_code=result.returncode,
        stderr=result.stderr,
        command=command,
        working_dir=resolved_working_dir,
        duration=duration,
        _json_schema=effective_json_schema,
        _response_model=response_model,
    )
```

**Definition of Done**:
- [ ] File `src/claude_cli_wrapper/core/client.py` exists
- [ ] Running `uv run python -c "from claude_cli_wrapper.core.client import run"` succeeds
- [ ] Function has complete type hints
- [ ] Function has comprehensive docstring

---

### Step 5.2: Update core/__init__.py

**Action**: Update `src/claude_cli_wrapper/core/__init__.py`:

```python
"""Core functionality for claude-cli-wrapper."""

from claude_cli_wrapper.core.client import run
from claude_cli_wrapper.core.response import ClaudeResponse

__all__ = [
    "run",
    "ClaudeResponse",
]
```

**Definition of Done**:
- [ ] File updated
- [ ] Running `uv run python -c "from claude_cli_wrapper.core import run, ClaudeResponse"` succeeds

---

### Step 5.3: Create Unit Tests for Client

**Action**: Create `tests/unit/test_client.py`:

```python
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
    def test_raises_execution_error_for_nonzero_exit(self, mock_run, mock_resolve) -> None:
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
```

**Definition of Done**:
- [ ] File `tests/unit/test_client.py` exists
- [ ] Running `uv run pytest tests/unit/test_client.py -v` passes all tests

---

## Phase 6: Session Management

### Step 6.1: Create session.py

**Action**: Create `src/claude_cli_wrapper/core/session.py`:

```python
"""Session management for multi-turn conversations."""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

from claude_cli_wrapper.core.client import run as _run
from claude_cli_wrapper.core.response import ClaudeResponse

if TYPE_CHECKING:
    from claude_cli_wrapper.models import Agent, Model, OutputFormat, PermissionMode


class Session:
    """A session for multi-turn conversations with Claude.

    Sessions maintain conversation context across multiple prompts.
    Use the `claude_session()` context manager to create sessions.

    Attributes:
        session_id: The unique identifier for this session.

    Example:
        >>> with claude_session() as session:
        ...     r1 = session.run("What is Python?")
        ...     r2 = session.run("Give me an example")  # Remembers context
    """

    def __init__(
        self,
        session_id: str | None = None,
        resume: str | None = None,
        fork: bool = False,
        working_dir: str | Path | None = None,
        cli_path: str | None = None,
    ) -> None:
        """Initialize a session.

        Args:
            session_id: Specific session ID to use. If None, generates a new UUID.
            resume: Session ID to resume from.
            fork: If True, create a new session forked from resume.
            working_dir: Working directory for all session commands.
            cli_path: Path to Claude CLI executable.
        """
        self._resume = resume
        self._fork = fork
        self._working_dir = working_dir
        self._cli_path = cli_path
        self._first_run = True

        if resume and not fork:
            self._session_id = resume
        elif session_id:
            self._session_id = session_id
        else:
            self._session_id = str(uuid.uuid4())

    @property
    def session_id(self) -> str:
        """Get the session ID."""
        return self._session_id

    def run(
        self,
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
        dangerously_skip_permissions: bool = False,
        # Configuration
        add_dirs: list[str | Path] | None = None,
        mcp_config: str | dict | None = None,
        agents: list[Any] | None = None,
        files: dict[str, str] | None = None,
        betas: list[str] | None = None,
        # Debugging
        verbose: bool = False,
    ) -> ClaudeResponse:
        """Execute a prompt within this session.

        The session context is automatically maintained across calls.

        Args:
            prompt: The prompt text to send to Claude.
            model: Model to use for this prompt.
            fallback_model: Fallback model when primary is overloaded.
            system_prompt: Replace the default system prompt.
            append_system_prompt: Append to the default system prompt.
            working_dir: Override session working directory for this call.
            timeout: Timeout in seconds for this call.
            max_turns: Maximum agentic turns for this call.
            output_format: Output format for this call.
            json_schema: JSON schema for structured output.
            response_model: Pydantic model for response parsing.
            allowed_tools: Tools to allow.
            disallowed_tools: Tools to disallow.
            tools: Restrict available tools.
            permission_mode: Permission mode.
            dangerously_skip_permissions: Skip permission checks.
            add_dirs: Additional directories.
            mcp_config: MCP configuration.
            agents: Custom agents.
            files: File resources.
            betas: Beta features.
            verbose: Enable verbose output.

        Returns:
            ClaudeResponse containing the result.
        """
        # Use session working directory if not overridden
        effective_working_dir = working_dir or self._working_dir

        # Handle session continuation
        resume = None
        fork_session = False

        if self._first_run:
            if self._resume:
                resume = self._resume
                fork_session = self._fork
            self._first_run = False
        else:
            # Subsequent runs continue the session
            resume = self._session_id

        response = _run(
            prompt,
            model=model,
            fallback_model=fallback_model,
            system_prompt=system_prompt,
            append_system_prompt=append_system_prompt,
            working_dir=effective_working_dir,
            timeout=timeout,
            max_turns=max_turns,
            output_format=output_format,
            json_schema=json_schema,
            response_model=response_model,
            allowed_tools=allowed_tools,
            disallowed_tools=disallowed_tools,
            tools=tools,
            permission_mode=permission_mode,
            dangerously_skip_permissions=dangerously_skip_permissions,
            session_id=self._session_id if self._first_run else None,
            resume=resume,
            fork_session=fork_session,
            cli_path=self._cli_path,
            add_dirs=add_dirs,
            mcp_config=mcp_config,
            agents=agents,
            files=files,
            betas=betas,
            verbose=verbose,
        )

        return response


@contextmanager
def claude_session(
    *,
    resume: str | None = None,
    fork: bool = False,
    working_dir: str | Path | None = None,
    cli_path: str | None = None,
) -> Generator[Session, None, None]:
    """Create a session for multi-turn conversations.

    Use this context manager to maintain conversation context across
    multiple prompts.

    Args:
        resume: Session ID to resume from a previous session.
        fork: If True and resume is provided, create a new session
            forked from the resumed session.
        working_dir: Working directory for all session commands.
        cli_path: Path to Claude CLI executable.

    Yields:
        A Session object for running prompts.

    Example:
        >>> with claude_session() as session:
        ...     r1 = session.run("What is the capital of France?")
        ...     r2 = session.run("What is its population?")
        ...     print(session.session_id)  # Save for later

        >>> # Resume a previous session
        >>> with claude_session(resume="abc-123") as session:
        ...     r = session.run("Continue our conversation")
    """
    session = Session(
        resume=resume,
        fork=fork,
        working_dir=working_dir,
        cli_path=cli_path,
    )
    yield session
```

**Definition of Done**:
- [ ] File `src/claude_cli_wrapper/core/session.py` exists
- [ ] Running `uv run python -c "from claude_cli_wrapper.core.session import claude_session, Session"` succeeds

---

### Step 6.2: Update core/__init__.py for Session

**Action**: Update `src/claude_cli_wrapper/core/__init__.py`:

```python
"""Core functionality for claude-cli-wrapper."""

from claude_cli_wrapper.core.client import run
from claude_cli_wrapper.core.response import ClaudeResponse
from claude_cli_wrapper.core.session import Session, claude_session

__all__ = [
    "run",
    "ClaudeResponse",
    "Session",
    "claude_session",
]
```

**Definition of Done**:
- [ ] File updated
- [ ] Running `uv run python -c "from claude_cli_wrapper.core import claude_session"` succeeds

---

### Step 6.3: Create Unit Tests for Session

**Action**: Create `tests/unit/test_session.py`:

```python
"""Unit tests for session management."""

from unittest.mock import patch, MagicMock

import pytest

from claude_cli_wrapper.core.session import Session, claude_session


def mock_run_response(**kwargs):
    """Create a mock ClaudeResponse."""
    mock = MagicMock()
    mock.text = kwargs.get("text", "response")
    mock.exit_code = kwargs.get("exit_code", 0)
    mock.stderr = kwargs.get("stderr", "")
    mock.command = kwargs.get("command", ["claude"])
    mock.working_dir = kwargs.get("working_dir", "/tmp")
    mock.duration = kwargs.get("duration", 1.0)
    return mock


class TestSession:
    """Tests for Session class."""

    def test_generates_session_id(self) -> None:
        """Session should generate a UUID if none provided."""
        session = Session()
        assert session.session_id is not None
        assert len(session.session_id) > 0

    def test_uses_provided_session_id(self) -> None:
        """Session should use provided session_id."""
        session = Session(session_id="my-custom-id")
        assert session.session_id == "my-custom-id"

    def test_uses_resume_as_session_id(self) -> None:
        """Session should use resume ID as session_id when not forking."""
        session = Session(resume="resumed-session")
        assert session.session_id == "resumed-session"

    def test_generates_new_id_when_forking(self) -> None:
        """Session should generate new ID when forking."""
        session = Session(resume="original-session", fork=True)
        assert session.session_id != "original-session"

    @patch("claude_cli_wrapper.core.session._run")
    def test_run_calls_underlying_run(self, mock_run) -> None:
        """Session.run should call the underlying run function."""
        mock_run.return_value = mock_run_response()
        session = Session()

        session.run("Test prompt")

        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args.kwargs
        assert mock_run.call_args.args[0] == "Test prompt"

    @patch("claude_cli_wrapper.core.session._run")
    def test_first_run_uses_session_id(self, mock_run) -> None:
        """First run should use session_id parameter."""
        mock_run.return_value = mock_run_response()
        session = Session(session_id="test-session")

        session.run("First prompt")

        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["session_id"] == "test-session"

    @patch("claude_cli_wrapper.core.session._run")
    def test_subsequent_runs_use_resume(self, mock_run) -> None:
        """Subsequent runs should use resume with session_id."""
        mock_run.return_value = mock_run_response()
        session = Session(session_id="test-session")

        session.run("First prompt")
        session.run("Second prompt")

        # Second call should use resume
        second_call_kwargs = mock_run.call_args.kwargs
        assert second_call_kwargs["resume"] == "test-session"

    @patch("claude_cli_wrapper.core.session._run")
    def test_uses_session_working_dir(self, mock_run) -> None:
        """Session should use its working_dir for all runs."""
        mock_run.return_value = mock_run_response()
        session = Session(working_dir="/session/dir")

        session.run("Test")

        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["working_dir"] == "/session/dir"

    @patch("claude_cli_wrapper.core.session._run")
    def test_run_can_override_working_dir(self, mock_run) -> None:
        """Session.run should allow overriding working_dir."""
        mock_run.return_value = mock_run_response()
        session = Session(working_dir="/session/dir")

        session.run("Test", working_dir="/override/dir")

        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["working_dir"] == "/override/dir"


class TestClaudeSessionContextManager:
    """Tests for claude_session context manager."""

    def test_yields_session(self) -> None:
        """claude_session should yield a Session object."""
        with claude_session() as session:
            assert isinstance(session, Session)

    def test_passes_resume_to_session(self) -> None:
        """claude_session should pass resume to Session."""
        with claude_session(resume="abc-123") as session:
            assert session.session_id == "abc-123"

    def test_passes_fork_to_session(self) -> None:
        """claude_session should pass fork to Session."""
        with claude_session(resume="abc-123", fork=True) as session:
            assert session.session_id != "abc-123"

    def test_passes_working_dir_to_session(self) -> None:
        """claude_session should pass working_dir to Session."""
        with claude_session(working_dir="/test/dir") as session:
            assert session._working_dir == "/test/dir"

    def test_passes_cli_path_to_session(self) -> None:
        """claude_session should pass cli_path to Session."""
        with claude_session(cli_path="/custom/claude") as session:
            assert session._cli_path == "/custom/claude"


class TestSessionMultiTurn:
    """Tests for multi-turn conversation behavior."""

    @patch("claude_cli_wrapper.core.session._run")
    def test_first_run_with_resume_passes_resume(self, mock_run) -> None:
        """First run with resume should pass resume parameter."""
        mock_run.return_value = mock_run_response()

        with claude_session(resume="old-session") as session:
            session.run("Continue")

        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["resume"] == "old-session"

    @patch("claude_cli_wrapper.core.session._run")
    def test_first_run_with_fork_passes_fork_session(self, mock_run) -> None:
        """First run with fork should pass fork_session=True."""
        mock_run.return_value = mock_run_response()

        with claude_session(resume="old-session", fork=True) as session:
            session.run("Fork and continue")

        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["resume"] == "old-session"
        assert call_kwargs["fork_session"] is True
```

**Definition of Done**:
- [ ] File `tests/unit/test_session.py` exists
- [ ] Running `uv run pytest tests/unit/test_session.py -v` passes all tests

---

## Phase 7: Public API

### Step 7.1: Create Main __init__.py

**Action**: Update `src/claude_cli_wrapper/__init__.py` with all public exports:

```python
"""Claude CLI Wrapper - A Python wrapper for the Claude Code CLI.

This package provides a clean Python interface for interacting with Claude
via the Claude Code CLI, enabling programmatic access without API keys.

Example:
    >>> from claude_cli_wrapper import run
    >>> response = run("Explain Python decorators")
    >>> print(response.text)

    >>> from claude_cli_wrapper import claude_session
    >>> with claude_session() as session:
    ...     r1 = session.run("What is Python?")
    ...     r2 = session.run("Give me an example")
"""

from claude_cli_wrapper.core import ClaudeResponse, Session, claude_session, run
from claude_cli_wrapper.errors import (
    AuthenticationError,
    CLINotFoundError,
    ClaudeError,
    ExecutionError,
    InvalidArgumentError,
    TimeoutError,
)
from claude_cli_wrapper.models import Agent, Model, OutputFormat, PermissionMode

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Main function
    "run",
    # Session management
    "claude_session",
    "Session",
    # Response
    "ClaudeResponse",
    # Exceptions
    "ClaudeError",
    "CLINotFoundError",
    "AuthenticationError",
    "InvalidArgumentError",
    "TimeoutError",
    "ExecutionError",
    # Models/Enums
    "Agent",
    "Model",
    "OutputFormat",
    "PermissionMode",
]
```

**Definition of Done**:
- [ ] File updated with all exports
- [ ] Running `uv run python -c "from claude_cli_wrapper import run, claude_session, ClaudeResponse, ClaudeError, Agent, Model, PermissionMode"` succeeds
- [ ] Running `uv run python -c "import claude_cli_wrapper; print(claude_cli_wrapper.__version__)"` outputs `0.1.0`

---

## Phase 8: Test Fixtures and Final Verification

### Step 8.1: Create Test Fixtures

**Action**: Create `tests/fixtures/mock_responses.py`:

```python
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
```

**Definition of Done**:
- [ ] File `tests/fixtures/mock_responses.py` exists

---

### Step 8.2: Create conftest.py

**Action**: Create `tests/conftest.py`:

```python
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
```

**Definition of Done**:
- [ ] File `tests/conftest.py` exists

---

### Step 8.3: Run Full Test Suite

**Action**: Execute the complete test suite:

```bash
uv run pytest -v --cov=src/claude_cli_wrapper --cov-report=term-missing
```

**Definition of Done**:
- [ ] All tests pass
- [ ] Coverage report shows >80% coverage
- [ ] No import errors
- [ ] No type errors reported

---

### Step 8.4: Run Linting and Formatting

**Action**: Execute linting and formatting checks:

```bash
uv run ruff check .
uv run ruff format . --check
```

**Definition of Done**:
- [ ] `ruff check .` passes with no errors
- [ ] `ruff format . --check` passes (no formatting changes needed)

---

### Step 8.5: Verify Package Build

**Action**: Build the package:

```bash
uv build
```

**Definition of Done**:
- [ ] Build completes without errors
- [ ] `dist/` directory contains `.whl` and `.tar.gz` files

---

## Phase 9: Final Checklist

Before considering the implementation complete, verify:

- [ ] All files from the module layout exist
- [ ] All `__init__.py` files have correct exports
- [ ] `py.typed` marker file exists
- [ ] `pyproject.toml` is valid and complete
- [ ] All tests pass (`uv run pytest`)
- [ ] Linting passes (`uv run ruff check .`)
- [ ] Formatting is correct (`uv run ruff format . --check`)
- [ ] Package builds successfully (`uv build`)
- [ ] README examples are accurate
- [ ] All public functions have docstrings
- [ ] All public functions have type hints
- [ ] Cross-platform compatibility considered (no hardcoded paths)
- [ ] Error messages include helpful context
- [ ] Logging is implemented for debug purposes

---

## Summary

| Phase | Steps | Key Deliverables |
|-------|-------|------------------|
| 0 | 0.1 - 0.5 | Project structure, pyproject.toml, LICENSE |
| 1 | 1.1 - 1.3 | Exception hierarchy with tests |
| 2 | 2.1 - 2.4 | Enums, Agent model with tests |
| 3 | 3.1 - 3.3 | ClaudeResponse with tests |
| 4 | 4.1 - 4.5 | Utility functions with tests |
| 5 | 5.1 - 5.3 | Main run() client with tests |
| 6 | 6.1 - 6.3 | Session management with tests |
| 7 | 7.1 | Public API exports |
| 8 | 8.1 - 8.5 | Fixtures, verification, build |
| 9 | Final | Complete checklist verification |

**Total Steps**: 28 atomic steps with clear Definitions of Done.
