# Deployment.md - Governance and Operations

> **Purpose**: This document defines the operational procedures for developing, testing, and deploying the `claude-cli-wrapper` package using `uv`.

---

## Prerequisites

### System Requirements

| Requirement | Minimum Version | Verification Command |
|-------------|-----------------|---------------------|
| Python | 3.10+ | `python --version` |
| uv | 0.4+ | `uv --version` |
| Claude CLI | Latest | `claude --version` |
| Node.js (for Claude CLI) | 18+ | `node --version` |

### Installing uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip (any platform)
pip install uv
```

### Installing Claude CLI

```bash
npm install -g @anthropic-ai/claude-code
```

---

## Development Environment Setup

### 1. Clone and Initialize

```bash
# Clone the repository
git clone https://github.com/your-username/claude-cli-wrapper.git
cd claude-cli-wrapper

# Create virtual environment with uv
uv venv

# Activate the virtual environment
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install all dependencies (including dev)
uv sync

# Install with optional pydantic support
uv sync --extra pydantic

# Install only production dependencies
uv sync --no-dev
```

### 3. Verify Installation

```bash
# Verify uv environment
uv run python --version

# Verify package is importable
uv run python -c "import claude_cli_wrapper; print('OK')"

# Run tests to confirm setup
uv run pytest
```

---

## Daily Development Workflow

### Adding Dependencies

```bash
# Add a runtime dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>

# Add with version constraint
uv add "pydantic>=2.0,<3.0"

# Add an optional dependency group
uv add --optional pydantic pydantic
```

### Removing Dependencies

```bash
# Remove a dependency
uv remove <package-name>

# Remove a dev dependency
uv remove --dev <package-name>
```

### Running Commands

```bash
# Run any command in the venv context
uv run <command>

# Examples:
uv run python script.py
uv run pytest tests/
uv run ruff check .
```

### Updating Dependencies

```bash
# Update all dependencies to latest compatible versions
uv sync --upgrade

# Update a specific package
uv add --upgrade <package-name>

# Regenerate lock file
uv lock --upgrade
```

---

## Code Quality Commands

### Linting

```bash
# Check for linting errors
uv run ruff check .

# Check and show fixes
uv run ruff check . --show-fixes

# Auto-fix linting errors
uv run ruff check . --fix
```

### Formatting

```bash
# Check formatting (dry run)
uv run ruff format . --check

# Apply formatting
uv run ruff format .
```

### Type Checking (Optional)

```bash
# If using mypy
uv add --dev mypy
uv run mypy src/
```

---

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_client.py

# Run specific test function
uv run pytest tests/unit/test_client.py::test_run_basic_prompt

# Run tests matching a pattern
uv run pytest -k "test_run"
```

### Test Coverage

```bash
# Run with coverage
uv run pytest --cov=src/claude_cli_wrapper

# Generate HTML coverage report
uv run pytest --cov=src/claude_cli_wrapper --cov-report=html

# View coverage report
# Linux: xdg-open htmlcov/index.html
# macOS: open htmlcov/index.html
# Windows: start htmlcov/index.html
```

### Test Markers

```bash
# Run only unit tests
uv run pytest tests/unit/

# Skip slow tests (if marked)
uv run pytest -m "not slow"
```

---

## Building and Publishing

### Building the Package

```bash
# Build source distribution and wheel
uv build

# Output will be in dist/
# dist/claude_cli_wrapper-0.1.0.tar.gz
# dist/claude_cli_wrapper-0.1.0-py3-none-any.whl
```

### Publishing to PyPI

```bash
# First, configure PyPI token (one-time setup)
# Create ~/.pypirc or use environment variable

# Publish to TestPyPI first (recommended)
uv publish --repository testpypi

# Publish to PyPI
uv publish
```

### Version Management

Version is defined in `pyproject.toml`:

```toml
[project]
version = "0.1.0"
```

Follow semantic versioning:
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

---

## CI/CD Pipeline

### GitHub Actions Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --dev

      - name: Lint
        run: uv run ruff check .

      - name: Format check
        run: uv run ruff format . --check

      - name: Test
        run: uv run pytest --cov=src/claude_cli_wrapper

  publish:
    needs: test
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Build
        run: uv build

      - name: Publish to PyPI
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: uv publish
```

---

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `CLAUDE_CLI_PATH` | Custom path to Claude CLI | `/opt/claude/bin/claude` |
| `UV_PUBLISH_TOKEN` | PyPI authentication token | `pypi-AgEIcHlw...` |

---

## Troubleshooting

### Common Issues

#### "uv: command not found"

```bash
# Reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or add to PATH manually
export PATH="$HOME/.cargo/bin:$PATH"
```

#### "No module named 'claude_cli_wrapper'"

```bash
# Ensure you're using uv run
uv run python -c "import claude_cli_wrapper"

# Or install in editable mode
uv sync
```

#### Lock file conflicts

```bash
# Regenerate lock file
uv lock --upgrade
```

#### Virtual environment issues

```bash
# Remove and recreate venv
rm -rf .venv
uv venv
uv sync
```

### Platform-Specific Notes

#### Windows

- Use `.venv\Scripts\activate` (not `source`)
- Use backslashes in paths or raw strings: `r"C:\path\to\file"`
- Claude CLI may be at `%APPDATA%\npm\claude.cmd`

#### Linux/macOS

- Use `source .venv/bin/activate`
- Claude CLI typically at `/usr/local/bin/claude` or `~/.npm-global/bin/claude`

---

## Quick Reference Card

```bash
# === Setup ===
uv venv                      # Create venv
uv sync                      # Install deps
uv sync --extra pydantic     # Install with optional deps

# === Development ===
uv add <pkg>                 # Add dependency
uv add --dev <pkg>           # Add dev dependency
uv remove <pkg>              # Remove dependency
uv run <cmd>                 # Run in venv

# === Quality ===
uv run ruff check .          # Lint
uv run ruff format .         # Format
uv run pytest                # Test
uv run pytest --cov=src      # Test with coverage

# === Build/Publish ===
uv build                     # Build package
uv publish                   # Publish to PyPI
```
