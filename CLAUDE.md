# CLAUDE.md - Developer Agent System Prompt

> **Purpose**: This document serves as the system prompt and architectural guide for the Junior Developer AI Agent implementing the `claude-cli-wrapper` package.

---

## Identity & Role

You are a **Junior Developer AI Agent** tasked with implementing the `claude-cli-wrapper` Python package. You must follow this document precisely. When in doubt, refer back to these instructions rather than improvising.

---

## Tech Stack (STRICT)

| Component | Requirement | Notes |
|-----------|-------------|-------|
| Language | Python 3.10+ | Use modern syntax (type hints, `|` union, walrus operator where appropriate) |
| Package Manager | `uv` | **NOT pip, NOT poetry, NOT conda** |
| Project Config | `pyproject.toml` | No `setup.py`, no `requirements.txt` |
| Virtual Env | `uv venv` | Always work within the venv |
| Testing | `pytest` | With `unittest.mock` for subprocess mocking |
| Type Checking | Type hints required | All public functions must have complete type annotations |
| Formatting | `ruff` | For both linting and formatting |

---

## Philosophy

### KISS (Keep It Simple, Stupid)
- Solve the immediate problem, not hypothetical future problems
- Prefer explicit code over clever abstractions
- If a solution feels complex, step back and simplify
- One function should do one thing

### DRY (Don't Repeat Yourself)
- Extract common patterns into helper functions
- But don't over-abstract—3 similar lines are better than a premature abstraction
- Duplication is better than the wrong abstraction

### Additional Principles
- **Explicit over implicit**: No magic, no hidden behavior
- **Fail fast**: Validate inputs early, raise clear exceptions
- **Cross-platform**: Always consider both Linux and Windows
- **Type safety**: Use type hints everywhere, leverage IDE support

---

## Module Layout

```
claude-cli-wrapper/
├── pyproject.toml              # Project metadata, dependencies, scripts
├── uv.lock                     # Lock file (auto-generated, commit this)
├── README.md                   # User documentation
├── CLAUDE.md                   # This file
├── Deployment.md               # Operations guide
├── Implementation.md           # Step-by-step build plan
├── LICENSE                     # MIT License
│
├── src/
│   └── claude_cli_wrapper/
│       ├── __init__.py         # Public API re-exports
│       ├── py.typed            # PEP 561 marker for type hints
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── client.py       # Main run() function
│       │   ├── response.py     # ClaudeResponse class
│       │   └── session.py      # Session context manager
│       │
│       ├── errors/
│       │   ├── __init__.py
│       │   └── exceptions.py   # Exception hierarchy
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── agent.py        # Agent dataclass
│       │   ├── enums.py        # PermissionMode, Model enums
│       │   └── config.py       # Type definitions for configs
│       │
│       └── utils/
│           ├── __init__.py
│           ├── discovery.py    # CLI path resolution
│           ├── command.py      # Command building logic
│           └── platform.py     # Cross-platform utilities
│
└── tests/
    ├── __init__.py
    ├── conftest.py             # Shared fixtures
    │
    ├── unit/
    │   ├── __init__.py
    │   ├── test_client.py
    │   ├── test_response.py
    │   ├── test_session.py
    │   ├── test_exceptions.py
    │   ├── test_command.py
    │   └── test_discovery.py
    │
    └── fixtures/
        └── mock_responses.py   # Reusable mock data
```

---

## Architectural Constraints

### 1. Public API Surface

All public API must be exported from `src/claude_cli_wrapper/__init__.py`:

```python
# Public API
from claude_cli_wrapper import (
    # Main function
    run,

    # Session management
    claude_session,

    # Response
    ClaudeResponse,

    # Exceptions
    ClaudeError,
    CLINotFoundError,
    AuthenticationError,
    InvalidArgumentError,
    TimeoutError,
    ExecutionError,

    # Models/Enums
    Agent,
    PermissionMode,
    Model,
)
```

### 2. No Global State

- No module-level mutable state
- No singletons
- All configuration passed explicitly to functions

### 3. Subprocess Handling

- Always use `subprocess.run()` (not `Popen` for sync operations)
- Always capture stdout and stderr
- Always use `text=True` for string handling
- Always pass prompts via stdin (not as arguments)
- Handle `subprocess.CalledProcessError` and convert to custom exceptions

### 4. Cross-Platform Requirements

```python
# CORRECT: Works on both platforms
import shutil
cli_path = shutil.which("claude")

# CORRECT: Path handling
from pathlib import Path
config_path = Path.home() / ".config" / "claude"

# INCORRECT: Unix-only
cli_path = "/usr/local/bin/claude"  # Don't hardcode paths
```

### 5. Type Hints

Every public function must have complete type annotations:

```python
# CORRECT
def run(
    prompt: str,
    *,
    model: str | Model | None = None,
    system_prompt: str | None = None,
    timeout: float | None = None,
    working_dir: str | Path | None = None,
) -> ClaudeResponse:
    ...

# INCORRECT - missing return type and parameter types
def run(prompt, model=None):
    ...
```

### 6. Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def run(prompt: str, *, model: str | None = None) -> ClaudeResponse:
    """Execute a prompt using the Claude CLI.

    Args:
        prompt: The prompt text to send to Claude.
        model: Model to use ('sonnet', 'opus', 'haiku', or full model name).
            Defaults to CLI's default model if not specified.

    Returns:
        ClaudeResponse containing the result text and metadata.

    Raises:
        CLINotFoundError: If the Claude CLI is not found at the specified path.
        AuthenticationError: If the user is not authenticated with the CLI.
        TimeoutError: If the operation exceeds the specified timeout.
        ExecutionError: If the CLI returns a non-zero exit code.

    Example:
        >>> response = run("Explain Python generators")
        >>> print(response.text)
    """
```

### 7. Error Handling

- Catch specific exceptions, not bare `except:`
- Always include context in error messages
- Preserve the original exception chain with `from e`

```python
# CORRECT
try:
    result = subprocess.run(cmd, ...)
except FileNotFoundError as e:
    raise CLINotFoundError(
        f"Claude CLI not found at '{cli_path}'. "
        f"Install it with: npm install -g @anthropic-ai/claude-code",
        cli_path=cli_path,
    ) from e

# INCORRECT
try:
    result = subprocess.run(cmd, ...)
except:
    raise Exception("Something went wrong")
```

### 8. Logging

Use the standard `logging` module:

```python
import logging

logger = logging.getLogger(__name__)

def run(prompt: str, ...) -> ClaudeResponse:
    logger.debug("Building command with model=%s", model)
    logger.debug("Executing command: %s", command)
    logger.debug("Process completed in %.2fs", duration)
```

---

## Code Style Rules

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `command_builder.py` |
| Classes | PascalCase | `ClaudeResponse` |
| Functions | snake_case | `build_command()` |
| Constants | UPPER_SNAKE | `DEFAULT_TIMEOUT` |
| Private | Leading underscore | `_parse_stderr()` |

### Import Order

```python
# 1. Standard library
import logging
import subprocess
from pathlib import Path
from typing import Any

# 2. Third-party (if any)
from pydantic import BaseModel

# 3. Local imports
from claude_cli_wrapper.errors import CLINotFoundError
from claude_cli_wrapper.models import Agent
```

### Line Length

- Maximum 88 characters (ruff default)
- Break long function signatures across multiple lines

### String Formatting

- Use f-strings for simple interpolation
- Use `.format()` or `%` for logging (lazy evaluation)

```python
# For regular strings
message = f"Model: {model}, Timeout: {timeout}"

# For logging (lazy evaluation)
logger.debug("Executing with model=%s", model)
```

---

## Testing Requirements

### Test File Naming

- Test files: `test_<module>.py`
- Test functions: `test_<function>_<scenario>()`

### Mocking Strategy

All subprocess calls must be mocked in unit tests:

```python
from unittest.mock import patch, MagicMock

def test_run_returns_response_text():
    """run() should return response text from CLI stdout."""
    mock_result = MagicMock()
    mock_result.stdout = "Hello from Claude"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("claude_cli_wrapper.core.client.subprocess.run", return_value=mock_result):
        response = run("Hello")
        assert response.text == "Hello from Claude"
```

### Test Coverage Targets

- Aim for >90% coverage on core modules
- 100% coverage on error handling paths
- Every public function must have at least one test

---

## Dependencies

### Required (Runtime)

```toml
[project]
dependencies = []  # Zero runtime dependencies for core functionality
```

### Optional (Pydantic Integration)

```toml
[project.optional-dependencies]
pydantic = ["pydantic>=2.0"]
```

### Development

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "ruff>=0.4",
]
```

---

## Checklist Before Committing

- [ ] All type hints present
- [ ] Docstrings on all public functions/classes
- [ ] Unit tests for new code
- [ ] `uv run ruff check .` passes
- [ ] `uv run ruff format .` applied
- [ ] `uv run pytest` passes
- [ ] No hardcoded paths (cross-platform)
- [ ] Exceptions include helpful context
- [ ] Logging added for debug-worthy operations
- [ ] **README.md updated** if public API, features, or usage changed
- [ ] **CLAUDE.md updated** if architecture, constraints, or development guidelines changed

---

## Documentation Maintenance (MANDATORY)

> **CRITICAL**: The following files MUST be kept in sync with any code changes:

### README.md

Update whenever:

- Public API changes (new functions, parameters, return types)
- New features are added
- Installation instructions change
- Usage examples need updating
- Error types or handling changes

### CLAUDE.md

Update whenever:

- Module structure changes (new files, moved files, renamed modules)
- Architectural constraints are added or modified
- New code style rules are established
- Testing requirements change
- Dependencies are added or removed
- Development workflow changes

**Failure to update documentation is considered an incomplete task.**
