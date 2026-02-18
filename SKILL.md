---
name: using-claude-cli-wrapper
description: Integrates the claude-cli-wrapper Python package to invoke Claude Code CLI programmatically. Covers one-shot prompts via run(), multi-turn sessions via claude_session(), structured output with JSON schemas or Pydantic models, tool control, custom agents, and error handling. Use when the project needs to call Claude from Python code.
---

# Using claude-cli-wrapper

## Prerequisites

- **Claude Code CLI** installed (`npm install -g @anthropic-ai/claude-code`) and authenticated (run `claude` once interactively to log in)
- **Python 3.10+**

## Installation

```bash
uv add git+https://github.com/rpakishore/claude-cli-wrapper.git
```

For Pydantic structured output, add `pydantic>=2.0` separately:

```bash
uv add git+https://github.com/rpakishore/claude-cli-wrapper.git pydantic
```

The package has zero runtime dependencies.

## Quick Reference

### One-shot prompt

```python
from claude_cli_wrapper import run

response = run("Explain Python generators in 2 sentences")
print(response.text)
```

### Multi-turn session

```python
from claude_cli_wrapper import claude_session

with claude_session() as session:
    r1 = session.run("What is the capital of France?")
    r2 = session.run("What is its population?")  # remembers context
    saved_id = session.session_id  # save for later
```

### Structured output (Pydantic)

```python
from pydantic import BaseModel
from claude_cli_wrapper import run

class Person(BaseModel):
    name: str
    age: int

response = run("Extract: 'Jane is 25 years old'", response_model=Person)
person = response.parsed  # typed Person instance
```

## `run()` Parameters

`run(prompt, *, ...)` is the main entry point. All keyword arguments are keyword-only.

### Model

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model` | `str \| None` | `None` | `"sonnet"`, `"opus"`, `"haiku"`, or full model name |
| `fallback_model` | `str \| None` | `None` | Fallback when primary model is overloaded |

### System prompt

| Parameter | Type | Default | Description |
|---|---|---|---|
| `system_prompt` | `str \| None` | `None` | Replace the default system prompt entirely |
| `append_system_prompt` | `str \| None` | `None` | Append text to the default system prompt |

### Execution

| Parameter | Type | Default | Description |
|---|---|---|---|
| `working_dir` | `str \| Path \| None` | `cwd` | Working directory for CLI execution |
| `timeout` | `float \| None` | `None` | Timeout in seconds (`None` = no timeout) |
| `max_turns` | `int \| None` | `None` | Maximum number of agentic turns |

### Output

| Parameter | Type | Default | Description |
|---|---|---|---|
| `output_format` | `str \| None` | `None` | `"text"`, `"json"`, or `"stream-json"` |
| `json_schema` | `dict \| None` | `None` | JSON schema for structured output validation |
| `response_model` | `type \| None` | `None` | Pydantic `BaseModel` subclass for response parsing |

### Tools

| Parameter | Type | Default | Description |
|---|---|---|---|
| `allowed_tools` | `list[str] \| None` | `None` | Whitelist of tools, e.g. `["Read", "Bash(git:*)"]` |
| `disallowed_tools` | `list[str] \| None` | `None` | Blacklist of tools to disallow |
| `tools` | `list[str] \| None` | `None` | Restrict available tools to exactly this list |

### Permissions

| Parameter | Type | Default | Description |
|---|---|---|---|
| `permission_mode` | `str \| None` | `None` | `"default"`, `"plan"`, `"acceptEdits"`, `"bypassPermissions"`, `"dontAsk"`, `"delegate"` |
| `dangerously_skip_permissions` | `bool` | `True` | Skip all permission checks (default `True` for non-interactive use) |

### Session

| Parameter | Type | Default | Description |
|---|---|---|---|
| `session_id` | `str \| None` | `None` | Use a specific session ID |
| `continue_session` | `bool` | `False` | Continue the most recent conversation |
| `resume` | `str \| None` | `None` | Resume a specific session by ID |
| `fork_session` | `bool` | `False` | Fork instead of continuing when resuming |
| `no_session_persistence` | `bool` | `False` | Disable session persistence |

### Configuration

| Parameter | Type | Default | Description |
|---|---|---|---|
| `cli_path` | `str \| None` | `None` | Path to Claude CLI (auto-discovered if `None`) |
| `add_dirs` | `list[str \| Path] \| None` | `None` | Additional directories to allow tool access |
| `mcp_config` | `str \| dict \| None` | `None` | Path to MCP config file or inline config dict |
| `agents` | `list[Agent] \| None` | `None` | Custom `Agent` objects for subagents |
| `files` | `dict[str, str] \| None` | `None` | Dict mapping `file_id` to relative path |
| `betas` | `list[str] \| None` | `None` | Beta features to enable |

### Debugging

| Parameter | Type | Default | Description |
|---|---|---|---|
| `verbose` | `bool` | `False` | Enable verbose CLI output |

## `ClaudeResponse`

Returned by `run()` and `Session.run()`. Supports `str(response)` which returns `response.text`.

| Attribute | Type | Description |
|---|---|---|
| `text` | `str` | The response text from Claude |
| `exit_code` | `int` | CLI process exit code (0 = success) |
| `stderr` | `str` | Any stderr output from the CLI |
| `command` | `list[str]` | The full command that was executed |
| `working_dir` | `str` | Working directory used for execution |
| `duration` | `float` | Execution time in seconds |
| `json` | `dict \| None` | Property. Parsed JSON; returns `None` unless `json_schema` or `response_model` was provided. Raises `ValueError` on invalid JSON. |
| `parsed` | `Any \| None` | Property. Validated Pydantic model instance; returns `None` unless `response_model` was provided. Raises `ImportError` if pydantic is not installed, `ValueError` on validation failure. |

## Sessions

`claude_session()` is a context manager that yields a `Session` object.

```python
claude_session(
    *,
    resume: str | None = None,      # session ID to resume
    fork: bool = False,              # fork from resumed session
    working_dir: str | Path | None = None,
    cli_path: str | None = None,
) -> Generator[Session, None, None]
```

`Session.run()` accepts the same keyword arguments as the top-level `run()` except for `session_id`, `continue_session`, `resume`, `fork_session`, and `no_session_persistence`—session state is managed automatically.

### Resume a session

```python
with claude_session(resume="abc-123") as session:
    r = session.run("Continue our conversation")
```

### Fork a session

```python
with claude_session(resume="abc-123", fork=True) as session:
    r = session.run("Try a different approach")
    # original session "abc-123" is unchanged
```

## Structured Output

### JSON schema (no extra dependencies)

```python
response = run(
    "Extract the person's name and age from: 'John is 30 years old'",
    json_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    },
)
data = response.json  # {"name": "John", "age": 30}
```

### Pydantic model (requires `pydantic` extra)

```python
from pydantic import BaseModel
from claude_cli_wrapper import run

class Person(BaseModel):
    name: str
    age: int

response = run("Extract: 'Jane is 25'", response_model=Person)
person = response.parsed  # Person(name='Jane', age=25)
print(person.name)        # "Jane"
```

When `response_model` is provided, the wrapper automatically sets `output_format="json"` and generates the JSON schema from the model. You do not need to set `json_schema` separately.

### JSON schema limitations

Schemas passed to `json_schema` (or generated from `response_model`) must follow [Anthropic's structured output constraints](https://platform.claude.com/docs/en/build-with-claude/structured-outputs#json-schema-limitations).

**Supported:** basic types (object, array, string, integer, number, boolean, null), `enum` (primitives only), `const`, `anyOf`/`allOf`, `$ref`/`$def`/`definitions` (no external `$ref`), `default`, `required`, `additionalProperties: false` (required on all objects), string formats (`date-time`, `time`, `date`, `duration`, `email`, `hostname`, `uri`, `ipv4`, `ipv6`, `uuid`), `minItems` (0 or 1 only).

**Not supported:** recursive schemas, complex types in enums, external `$ref`, numerical constraints (`minimum`, `maximum`, `multipleOf`), string constraints (`minLength`, `maxLength`), array constraints beyond `minItems` 0/1, `additionalProperties` set to anything other than `false`.

## Tool Control

```python
# Whitelist specific tools
response = run("Analyze this codebase", allowed_tools=["Read", "Grep", "Glob"])

# Blacklist specific tools
response = run("Suggest improvements", disallowed_tools=["Edit", "Write", "Bash"])

# Granular Bash permissions
response = run("Check git status", allowed_tools=["Bash(git:*)", "Read"])

# Restrict to exactly these tools (nothing else available)
response = run("Read the README", tools=["Read"])
```

## Custom Agents

```python
from claude_cli_wrapper import run, Agent

reviewer = Agent(
    name="code-reviewer",
    description="Expert code reviewer for Python projects",
    prompt="You are a senior Python developer. Focus on code quality and security.",
    tools=["Read", "Grep", "Glob"],  # None = inherit all tools
    model="sonnet",                   # None = use default model
)

response = run("Review the authentication module", agents=[reviewer])
```

`Agent` is a dataclass with fields: `name` (str, required), `description` (str, required), `prompt` (str, required), `tools` (list[str] | None), `model` (str | None).

## Error Handling

Exception hierarchy:

```
ClaudeError                  # base; has .message
├── CLINotFoundError         # has .cli_path
├── AuthenticationError      # (no extra attrs)
├── InvalidArgumentError     # has .argument, .value (both optional)
├── TimeoutError             # has .timeout, .command (optional)
└── ExecutionError           # has .exit_code, .stderr, .command (all optional except exit_code)
```

Usage:

```python
from claude_cli_wrapper import (
    run, ClaudeError, CLINotFoundError, AuthenticationError,
    InvalidArgumentError, TimeoutError, ExecutionError,
)

try:
    response = run("Hello", timeout=30)
except CLINotFoundError as e:
    print(f"CLI not found at: {e.cli_path}")
except AuthenticationError:
    print("Run 'claude' interactively to log in")
except TimeoutError as e:
    print(f"Timed out after {e.timeout}s")
except InvalidArgumentError as e:
    print(f"Bad argument: {e.argument}={e.value}")
except ExecutionError as e:
    print(f"Exit code {e.exit_code}: {e.stderr}")
except ClaudeError as e:
    print(f"Unexpected: {e.message}")
```

## Key Caveats

1. **`dangerously_skip_permissions=True` by default** — the wrapper is designed for non-interactive use. Set to `False` only if you can handle interactive permission prompts.
2. **Prompts are sent via stdin**, not as CLI arguments. This avoids shell escaping issues and argument length limits.
3. **`--print` flag is always added** — the CLI runs in non-interactive print mode. Do not expect interactive behavior.
4. **CLI path resolution order**: explicit `cli_path` parameter, then `CLAUDE_CLI_PATH` environment variable, then system `PATH` lookup via `shutil.which`.
5. **Cross-platform**: on Windows the CLI is discovered as `claude.cmd`; on Unix as `claude`.
6. **`.json` returns `None`** unless `json_schema` or `response_model` was provided to `run()`.
7. **`.parsed` returns `None`** unless `response_model` was provided. Requires the `pydantic` extra to be installed.
8. **`response_model` must be a Pydantic `BaseModel` subclass** — passing a plain dataclass or dict raises `InvalidArgumentError`.
9. **All `run()` keyword arguments are keyword-only** — positional usage beyond `prompt` is not supported.
10. **`Model`, `PermissionMode`, `OutputFormat` enums** are `str` enums — you can pass either the enum member or its string value (e.g., `Model.OPUS` or `"opus"`).
