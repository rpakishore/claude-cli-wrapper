# claude-cli-wrapper

A Python wrapper for the [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code), enabling programmatic access to Claude without API keys.

## Motivation

Claude Max subscribers get virtually unlimited Claude Code CLI usage but no API access. This package bridges that gap by wrapping the CLI in a clean Python interface, allowing you to:

- Use Claude in Python scripts and automation
- Build tools and workflows powered by Claude
- Avoid per-token API costs with your Max subscription

## Features

- **Simple API**: Single `run()` function for one-shot prompts
- **Session Management**: Context manager for multi-turn conversations
- **Full CLI Parity**: Access to all Claude CLI flags and options
- **Cross-Platform**: Works on Linux and Windows
- **Type-Safe**: Complete type hints with IDE autocomplete
- **Pydantic Integration**: Optional structured output with Pydantic models
- **Rich Errors**: Detailed exception hierarchy with helpful context

## Installation

```bash
pip install claude-cli-wrapper
```

Or with `uv`:

```bash
uv add claude-cli-wrapper
```

### Optional: Pydantic Support

For structured output with Pydantic models:

```bash
pip install claude-cli-wrapper[pydantic]
```

### Prerequisites

1. **Claude Code CLI** must be installed:

   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Authenticate** the CLI (one-time):

   ```bash
   claude
   # Follow the prompts to log in
   ```

## Quick Start

### Basic Usage

```python
from claude_cli_wrapper import run

# Simple prompt
response = run("Explain Python generators in 2 sentences")
print(response.text)
```

### Specifying a Model

```python
from claude_cli_wrapper import run, Model

# Using enum
response = run("Write a haiku about coding", model=Model.OPUS)

# Or using string
response = run("Write a haiku about coding", model="opus")
```

### Custom System Prompt

```python
response = run(
    "Review this code for bugs",
    system_prompt="You are a senior Python developer. Be concise and direct.",
)
```

### Working Directory

```python
response = run(
    "Explain what this project does",
    working_dir="/path/to/project",
)
```

### Timeout

```python
response = run(
    "Refactor this entire codebase",
    timeout=600,  # 10 minutes
)
```

## Session Management

For multi-turn conversations, use the context manager:

```python
from claude_cli_wrapper import claude_session

with claude_session() as session:
    r1 = session.run("What is the capital of France?")
    print(r1.text)  # "Paris"

    r2 = session.run("What is its population?")
    print(r2.text)  # Knows we're talking about Paris

    # Save session ID for later
    print(f"Session ID: {session.session_id}")
```

### Resuming Sessions

```python
# Resume a previous session
with claude_session(resume="abc-123-def") as session:
    response = session.run("Continue where we left off")
```

### Forking Sessions

```python
# Fork to try a different approach without losing original
with claude_session(resume="abc-123-def", fork=True) as session:
    response = session.run("Let's try a different approach")
```

## Response Object

The `ClaudeResponse` object provides rich metadata:

```python
response = run("Hello")

# Core content
print(response.text)        # The response text
print(str(response))        # Same as response.text

# Metadata
print(response.exit_code)   # CLI exit code (0 = success)
print(response.stderr)      # Any stderr output
print(response.command)     # The full command that was executed
print(response.working_dir) # Working directory used
print(response.duration)    # Execution time in seconds
print(response.metadata)    # CLI metadata (when output_format="json")
```

## Structured Output (JSON Schema)

### With Dictionary Schema

```python
response = run(
    "Extract the person's name and age from: 'John is 30 years old'",
    json_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name", "age"]
    }
)

# Parsed automatically
print(response.json)  # {"name": "John", "age": 30}
```

### With Pydantic Models

```python
from pydantic import BaseModel
from claude_cli_wrapper import run

class Person(BaseModel):
    name: str
    age: int

response = run(
    "Extract: 'Jane is 25 years old'",
    response_model=Person,
)

# Typed Pydantic instance
person = response.parsed
print(person.name)  # "Jane"
print(person.age)   # 25
```

### Response Metadata

When using JSON output, the CLI returns metadata alongside the response:

```python
response = run(
    "Extract name from: 'Alice is 30'",
    json_schema={"type": "object", "properties": {"name": {"type": "string"}}},
)

if response.metadata:
    print(response.metadata["session_id"])      # Session identifier
    print(response.metadata["total_cost_usd"])  # Cost in USD
    print(response.metadata["num_turns"])        # Agentic turns used
    print(response.metadata["duration_ms"])      # CLI duration in ms
```

## Tool Control

Restrict which tools Claude can use:

```python
# Only allow read operations
response = run(
    "Analyze this codebase",
    allowed_tools=["Read", "Grep", "Glob"],
)

# Disallow file modifications
response = run(
    "Suggest improvements",
    disallowed_tools=["Edit", "Write", "Bash"],
)

# Granular Bash permissions
response = run(
    "Check git status",
    allowed_tools=["Bash(git:*)", "Read"],
)
```

## Custom Agents

Define specialized subagents:

```python
from claude_cli_wrapper import run, Agent

reviewer = Agent(
    name="code-reviewer",
    description="Expert code reviewer for Python projects",
    prompt="You are a senior Python developer. Focus on code quality, security, and best practices.",
    tools=["Read", "Grep", "Glob"],
    model="sonnet",
)

response = run(
    "Review the authentication module",
    agents=[reviewer],
)
```

## MCP Configuration

Connect to MCP servers for extended capabilities:

```python
# From a config file
response = run(
    "Query the database",
    mcp_config="/path/to/mcp.json",
)

# Or inline configuration
response = run(
    "Query the database",
    mcp_config={
        "mcpServers": {
            "sqlite": {
                "command": "uvx",
                "args": ["mcp-server-sqlite", "--db-path", "data.db"]
            }
        }
    },
)
```

## Permission Modes

Control how Claude handles permissions:

```python
from claude_cli_wrapper import run, PermissionMode

# Plan mode - Claude explains before acting
response = run("Refactor this module", permission_mode=PermissionMode.PLAN)

# Auto-accept edits (use with caution)
response = run("Fix the typo", permission_mode=PermissionMode.ACCEPT_EDITS)
```

> **Note**: By default, `dangerously_skip_permissions=True` is set to enable
> non-interactive usage. Set it to `False` if you want permission prompts:

```python
response = run(
    "Run the build",
    dangerously_skip_permissions=False,  # Enable permission prompts
)
```

## Advanced Options

### All Parameters

```python
response = run(
    prompt="Your prompt here",

    # Model
    model="opus",                          # sonnet, opus, haiku, or full name
    fallback_model="sonnet",               # Fallback if primary is overloaded

    # System prompts
    system_prompt="Custom system prompt",  # Replace default
    append_system_prompt="Extra rules",    # Append to default

    # Execution
    working_dir="/path/to/project",        # Working directory
    timeout=300,                           # Timeout in seconds
    max_turns=10,                          # Limit agentic turns

    # Tools
    allowed_tools=["Read", "Grep"],        # Whitelist tools
    disallowed_tools=["Bash"],             # Blacklist tools
    tools=["Read", "Edit"],                # Restrict available tools

    # Output
    output_format="json",                  # text, json, stream-json
    json_schema={...},                     # JSON schema validation
    response_model=MyPydanticModel,        # Pydantic model

    # Session
    session_id="uuid-here",                # Use specific session
    continue_session=True,                 # Continue most recent
    resume="session-id",                   # Resume specific session
    fork_session=True,                     # Fork instead of continue

    # Permissions
    permission_mode=PermissionMode.PLAN,
    dangerously_skip_permissions=True,     # Default: True (non-interactive)

    # Configuration
    cli_path="/custom/path/claude",        # Custom CLI path
    add_dirs=["/extra/dir1", "/extra/dir2"],
    mcp_config="/path/to/mcp.json",
    agents=[agent1, agent2],
    betas=["beta-feature"],

    # Files
    files={"file_abc": "doc.pdf"},

    # Debugging
    verbose=True,
)
```

## Error Handling

```python
from claude_cli_wrapper import (
    run,
    ClaudeError,
    CLINotFoundError,
    AuthenticationError,
    InvalidArgumentError,
    TimeoutError,
    ExecutionError,
)

try:
    response = run("Hello", timeout=10)
except CLINotFoundError as e:
    print(f"CLI not found at: {e.cli_path}")
    print("Install with: npm install -g @anthropic-ai/claude-code")
except AuthenticationError as e:
    print("Not logged in. Run 'claude' to authenticate.")
except TimeoutError as e:
    print(f"Timed out after {e.timeout}s")
except InvalidArgumentError as e:
    print(f"Invalid argument: {e}")
except ExecutionError as e:
    print(f"CLI error (exit code {e.exit_code}): {e.stderr}")
except ClaudeError as e:
    print(f"Unexpected error: {e}")
```

## CLI Path Configuration

By default, the wrapper looks for `claude` in your PATH. For custom installations:

```python
# Via parameter
response = run("Hello", cli_path="/custom/path/claude")

# Via environment variable
import os
os.environ["CLAUDE_CLI_PATH"] = "/custom/path/claude"
response = run("Hello")
```

## Logging

Enable debug logging to see what's happening:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("claude_cli_wrapper").setLevel(logging.DEBUG)

response = run("Hello")
# DEBUG:claude_cli_wrapper.core.client:Building command...
# DEBUG:claude_cli_wrapper.core.client:Executing: ['claude', '-p', ...]
# DEBUG:claude_cli_wrapper.core.client:Completed in 2.34s
```

## API Reference

### `run(prompt, **kwargs) -> ClaudeResponse`

Execute a single prompt and return the response.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | *required* | The prompt text to send to Claude |
| `model` | `str \| Model` | `None` | Model to use: `"sonnet"`, `"opus"`, `"haiku"`, or full model name |
| `fallback_model` | `str` | `None` | Fallback model when primary is overloaded |
| `system_prompt` | `str` | `None` | Replace the default system prompt entirely |
| `append_system_prompt` | `str` | `None` | Append text to the default system prompt |
| `working_dir` | `str \| Path` | `cwd` | Working directory for CLI execution |
| `timeout` | `float` | `None` | Timeout in seconds (None = no timeout) |
| `max_turns` | `int` | `None` | Maximum number of agentic turns |
| `output_format` | `str` | `None` | Output format: `"text"`, `"json"`, `"stream-json"` |
| `json_schema` | `dict` | `None` | JSON schema for structured output validation |
| `response_model` | `type` | `None` | Pydantic model for response parsing |
| `allowed_tools` | `list[str]` | `None` | Whitelist of tools to allow |
| `disallowed_tools` | `list[str]` | `None` | Blacklist of tools to disallow |
| `tools` | `list[str]` | `None` | Restrict available tools to this list |
| `permission_mode` | `str \| PermissionMode` | `None` | Permission mode for the session |
| `dangerously_skip_permissions` | `bool` | `True` | Skip all permission checks |
| `session_id` | `str` | `None` | Use a specific session ID |
| `continue_session` | `bool` | `False` | Continue the most recent conversation |
| `resume` | `str` | `None` | Resume a specific session by ID |
| `fork_session` | `bool` | `False` | Create new session when resuming |
| `no_session_persistence` | `bool` | `False` | Disable session persistence |
| `cli_path` | `str` | `None` | Path to Claude CLI (auto-discovered if None) |
| `add_dirs` | `list[str \| Path]` | `None` | Additional directories to allow tool access |
| `mcp_config` | `str \| dict` | `None` | Path to MCP config file or config dict |
| `agents` | `list[Agent]` | `None` | List of custom Agent objects |
| `files` | `dict[str, str]` | `None` | Dict mapping file_id to relative_path |
| `betas` | `list[str]` | `None` | List of beta features to enable |
| `verbose` | `bool` | `False` | Enable verbose CLI output |

### `claude_session(**kwargs) -> Generator[Session]`

Context manager for multi-turn conversations.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `resume` | `str` | `None` | Session ID to resume from |
| `fork` | `bool` | `False` | Create a new session forked from the resumed session |
| `working_dir` | `str \| Path` | `None` | Working directory for all session commands |
| `cli_path` | `str` | `None` | Path to Claude CLI executable |

### `ClaudeResponse`

Response object returned by `run()` and `Session.run()`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `text` | `str` | The response text from Claude |
| `exit_code` | `int` | CLI process exit code (0 = success) |
| `stderr` | `str` | Any stderr output from the CLI |
| `command` | `list[str]` | The full command that was executed |
| `working_dir` | `str` | The working directory used |
| `duration` | `float` | Execution time in seconds |
| `metadata` | `dict \| None` | CLI envelope metadata (session_id, cost, usage, etc.) when `output_format="json"` |
| `json` | `dict \| None` | Parsed JSON (when json_schema was provided) |
| `parsed` | `Any \| None` | Pydantic model instance (when response_model was provided) |

### `Agent`

Custom subagent definition.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | *required* | Unique identifier for the agent |
| `description` | `str` | *required* | When to use this agent |
| `prompt` | `str` | *required* | System prompt for the agent |
| `tools` | `list[str]` | `None` | Tools the agent can use (None = inherit all) |
| `model` | `str` | `None` | Model alias (None = use default) |

### Enums

#### `Model`
- `Model.SONNET` - `"sonnet"`
- `Model.OPUS` - `"opus"`
- `Model.HAIKU` - `"haiku"`

#### `PermissionMode`
- `PermissionMode.DEFAULT` - `"default"`
- `PermissionMode.PLAN` - `"plan"`
- `PermissionMode.ACCEPT_EDITS` - `"acceptEdits"`
- `PermissionMode.BYPASS_PERMISSIONS` - `"bypassPermissions"`
- `PermissionMode.DONT_ASK` - `"dontAsk"`
- `PermissionMode.DELEGATE` - `"delegate"`

#### `OutputFormat`
- `OutputFormat.TEXT` - `"text"`
- `OutputFormat.JSON` - `"json"`
- `OutputFormat.STREAM_JSON` - `"stream-json"`

### Exceptions

All exceptions inherit from `ClaudeError`:

| Exception | Description |
|-----------|-------------|
| `ClaudeError` | Base exception for all wrapper errors |
| `CLINotFoundError` | Claude CLI executable not found |
| `AuthenticationError` | User not authenticated with CLI |
| `InvalidArgumentError` | Invalid arguments passed to CLI |
| `TimeoutError` | Operation exceeded timeout |
| `ExecutionError` | CLI returned non-zero exit code |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read [CLAUDE.md](CLAUDE.md) for development guidelines.
