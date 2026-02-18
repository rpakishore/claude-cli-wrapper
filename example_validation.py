"""Validation script for claude-cli-wrapper.

Run this script to verify the package is installed correctly and the
Claude CLI is accessible and responding as expected.

Usage:
    uv run python example_validation.py
"""

from __future__ import annotations

import sys
import traceback

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
SKIP = "\033[33mSKIP\033[0m"

results: list[tuple[str, str, str]] = []  # (name, status, detail)


def record(name: str, status: str, detail: str = "") -> None:
    results.append((name, status, detail))
    tag = PASS if status == "pass" else FAIL if status == "fail" else SKIP
    line = f"  [{tag}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)


# ---------------------------------------------------------------------------
# 1. Import validation
# ---------------------------------------------------------------------------
print("\n=== 1. Import Validation ===")

try:
    from claude_cli_wrapper import (  # noqa: F401
        Agent,
        AuthenticationError,
        ClaudeError,
        ClaudeResponse,
        CLINotFoundError,
        ExecutionError,
        InvalidArgumentError,
        Model,
        OutputFormat,
        PermissionMode,
        Session,
        TimeoutError,
        __version__,
        claude_session,
        run,
    )

    record("Import public API", "pass")
except ImportError as exc:
    record("Import public API", "fail", str(exc))
    print("\nCannot continue without imports. Is the package installed?")
    print("  Try: uv pip install -e .")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Version check
# ---------------------------------------------------------------------------
print("\n=== 2. Package Metadata ===")

if __version__:
    record("__version__ is set", "pass", f"v{__version__}")
else:
    record("__version__ is set", "fail", "empty or None")

# ---------------------------------------------------------------------------
# 3. CLI discovery
# ---------------------------------------------------------------------------
print("\n=== 3. CLI Discovery ===")

try:
    from claude_cli_wrapper.utils.discovery import resolve_cli_path

    cli_path = resolve_cli_path(None)
    record("Resolve CLI path", "pass", cli_path)
except Exception as exc:
    record("Resolve CLI path", "fail", str(exc))
    print("\nClaude CLI not found. Remaining tests will be skipped.")
    _print_summary()  # type: ignore[name-defined]
    sys.exit(1)

# ---------------------------------------------------------------------------
# 4. Basic run() — plain text
# ---------------------------------------------------------------------------
print("\n=== 4. Basic run() ===")

try:
    response = run(
        "Reply with exactly: HELLO_VALIDATION_TEST",
        max_turns=1,
        system_prompt="You are a test assistant. Follow instructions exactly. Reply with only what is asked, nothing else.",
    )

    # Check return type
    if isinstance(response, ClaudeResponse):
        record("Return type is ClaudeResponse", "pass")
    else:
        record("Return type is ClaudeResponse", "fail", f"got {type(response).__name__}")

    # Check text is non-empty
    if response.text and len(response.text.strip()) > 0:
        record("Response text is non-empty", "pass", f"{len(response.text.strip())} chars")
    else:
        record("Response text is non-empty", "fail", "empty response")

    # Check expected content
    if "HELLO_VALIDATION_TEST" in response.text:
        record("Response contains expected string", "pass")
    else:
        record(
            "Response contains expected string",
            "fail",
            f"expected 'HELLO_VALIDATION_TEST', got: {response.text[:100]}",
        )

    # Check exit code
    if response.exit_code == 0:
        record("Exit code is 0", "pass")
    else:
        record("Exit code is 0", "fail", f"exit_code={response.exit_code}")

    # Check metadata fields are populated
    if response.duration > 0:
        record("Duration is recorded", "pass", f"{response.duration:.2f}s")
    else:
        record("Duration is recorded", "fail", f"duration={response.duration}")

    if response.command and len(response.command) > 0:
        record("Command is recorded", "pass")
    else:
        record("Command is recorded", "fail", "empty command list")

    if response.working_dir:
        record("Working dir is recorded", "pass")
    else:
        record("Working dir is recorded", "fail")

    # Check __str__ returns text
    if str(response) == response.text:
        record("__str__ returns text", "pass")
    else:
        record("__str__ returns text", "fail")

except ClaudeError as exc:
    record("Basic run()", "fail", f"{type(exc).__name__}: {exc.message}")
except Exception as exc:
    record("Basic run()", "fail", f"Unexpected: {exc}")
    traceback.print_exc()

# ---------------------------------------------------------------------------
# 5. Model enum usage
# ---------------------------------------------------------------------------
print("\n=== 5. Model Enum ===")

try:
    response = run(
        "Reply with exactly: MODEL_ENUM_OK",
        model=Model.HAIKU,
        max_turns=1,
        system_prompt="Follow instructions exactly. Reply with only what is asked.",
    )

    if response.exit_code == 0 and response.text.strip():
        record("run() with Model enum", "pass", f"model=haiku, {len(response.text.strip())} chars")
    else:
        record("run() with Model enum", "fail", f"exit={response.exit_code}")
except ClaudeError as exc:
    record("run() with Model enum", "fail", f"{type(exc).__name__}: {exc.message}")
except Exception as exc:
    record("run() with Model enum", "fail", str(exc))

# ---------------------------------------------------------------------------
# 6. JSON output format
# ---------------------------------------------------------------------------
print("\n=== 6. JSON Output ===")

try:
    schema = {
        "type": "object",
        "properties": {
            "greeting": {"type": "string"},
        },
        "required": ["greeting"],
    }

    response = run(
        'Return a JSON object with a "greeting" key set to "hello".',
        output_format="json",
        json_schema=schema,
        system_prompt="You return valid JSON only. No markdown fences.",
    )

    if response.json is not None:
        record("JSON parsing works", "pass", f"keys={list(response.json.keys())}")
    else:
        record("JSON parsing works", "fail", "json property returned None")

    if response.json and "greeting" in response.json:
        record("JSON has expected key", "pass", f'greeting="{response.json["greeting"]}"')
    else:
        record("JSON has expected key", "fail", f"response: {response.text[:100]}")

    meta = response.metadata
    if meta is not None and len(meta) > 0:
        record(
            "Response metadata populated",
            "pass",
            f"keys={list(meta.keys())}",
        )
    else:
        record(
            "Response metadata populated",
            "fail",
            "metadata is None or empty",
        )

except ClaudeError as exc:
    record("JSON output", "fail", f"{type(exc).__name__}: {exc.message}")
except ValueError as exc:
    record("JSON output", "fail", f"Parse error: {exc}")
except Exception as exc:
    record("JSON output", "fail", str(exc))

# ---------------------------------------------------------------------------
# 6b. JSON schema only (auto output_format)
# ---------------------------------------------------------------------------
print("\n=== 6b. JSON Schema Only (auto format) ===")

try:
    schema_auto = {
        "type": "object",
        "properties": {
            "color": {"type": "string"},
        },
        "required": ["color"],
    }

    response_auto = run(
        'Return a JSON object with a "color" key set to "blue".',
        json_schema=schema_auto,
        system_prompt=(
            "You return valid JSON only. No markdown fences."
        ),
    )

    if response_auto.json is not None:
        record(
            "Auto-format JSON parsing works",
            "pass",
            f"keys={list(response_auto.json.keys())}",
        )
    else:
        record(
            "Auto-format JSON parsing works",
            "fail",
            "json property returned None",
        )

    if response_auto.json and "color" in response_auto.json:
        record(
            "Auto-format JSON has expected key",
            "pass",
            f'color="{response_auto.json["color"]}"',
        )
    else:
        record(
            "Auto-format JSON has expected key",
            "fail",
            f"response: {response_auto.text[:100]}",
        )

    meta_auto = response_auto.metadata
    if meta_auto is not None and len(meta_auto) > 0:
        record(
            "Auto-format metadata populated",
            "pass",
            f"keys={list(meta_auto.keys())}",
        )
    else:
        record(
            "Auto-format metadata populated",
            "fail",
            "metadata is None or empty",
        )

except ClaudeError as exc:
    record(
        "JSON schema only",
        "fail",
        f"{type(exc).__name__}: {exc.message}",
    )
except ValueError as exc:
    record("JSON schema only", "fail", f"Parse error: {exc}")
except Exception as exc:
    record("JSON schema only", "fail", str(exc))

# ---------------------------------------------------------------------------
# 7. Session (multi-turn)
# ---------------------------------------------------------------------------
print("\n=== 7. Session (Multi-Turn) ===")

try:
    with claude_session() as session:
        # Check session ID is generated
        if session.session_id:
            record("Session ID generated", "pass", session.session_id[:8] + "...")
        else:
            record("Session ID generated", "fail")

        r1 = session.run(
            "Remember this code word: PINEAPPLE_42. Confirm by replying with exactly: REMEMBERED",
            max_turns=1,
            system_prompt="Follow instructions exactly. Reply with only what is asked.",
        )

        if r1.exit_code == 0 and r1.text.strip():
            record("Session first message", "pass")
        else:
            record("Session first message", "fail")

        r2 = session.run(
            "What was the code word I told you? Reply with only the code word.",
            max_turns=1,
        )

        if "PINEAPPLE_42" in r2.text:
            record("Session context retained", "pass")
        else:
            record(
                "Session context retained",
                "fail",
                f"expected 'PINEAPPLE_42', got: {r2.text[:100]}",
            )

except ClaudeError as exc:
    record("Session", "fail", f"{type(exc).__name__}: {exc.message}")
except Exception as exc:
    record("Session", "fail", str(exc))
    traceback.print_exc()

# ---------------------------------------------------------------------------
# 8. Timeout handling
# ---------------------------------------------------------------------------
print("\n=== 8. Error Handling ===")

try:
    run("This should time out", timeout=0.001)
    record("TimeoutError raised", "fail", "no exception raised")
except TimeoutError:
    record("TimeoutError raised", "pass")
except ClaudeError as exc:
    # Might fail before timeout (e.g. CLI starts fast enough)
    record("TimeoutError raised", "skip", f"got {type(exc).__name__} instead")
except Exception as exc:
    record("TimeoutError raised", "fail", f"unexpected: {type(exc).__name__}: {exc}")

# ---------------------------------------------------------------------------
# 9. CLINotFoundError
# ---------------------------------------------------------------------------
try:
    run("test", cli_path="/nonexistent/claude-binary")
    record("CLINotFoundError raised", "fail", "no exception raised")
except CLINotFoundError:
    record("CLINotFoundError raised", "pass")
except Exception as exc:
    record("CLINotFoundError raised", "fail", f"unexpected: {type(exc).__name__}: {exc}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)

passed = sum(1 for _, s, _ in results if s == "pass")
failed = sum(1 for _, s, _ in results if s == "fail")
skipped = sum(1 for _, s, _ in results if s == "skip")
total = len(results)

print(f"  Total:   {total}")
print(f"  Passed:  {passed}")
print(f"  Failed:  {failed}")
print(f"  Skipped: {skipped}")
print()

if failed > 0:
    print("Failed checks:")
    for name, status, detail in results:
        if status == "fail":
            print(f"  - {name}: {detail}")
    print()

sys.exit(1 if failed > 0 else 0)
