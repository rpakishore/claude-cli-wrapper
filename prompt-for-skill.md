# Prompt: Update SKILL.md

> Copy-paste this entire prompt into Claude Code to regenerate `SKILL.md` from the current source code.

---

Read the following source files, then regenerate `SKILL.md` at the repository root so it accurately reflects the current API:

1. `src/claude_cli_wrapper/__init__.py` — public API exports
2. `src/claude_cli_wrapper/core/client.py` — `run()` signature and docstring
3. `src/claude_cli_wrapper/core/session.py` — `claude_session()` and `Session` class
4. `src/claude_cli_wrapper/core/response.py` — `ClaudeResponse` dataclass
5. `src/claude_cli_wrapper/errors/exceptions.py` — exception hierarchy and attributes
6. `src/claude_cli_wrapper/models/enums.py` — `Model`, `PermissionMode`, `OutputFormat`
7. `src/claude_cli_wrapper/models/agent.py` — `Agent` dataclass

## SKILL.md Requirements

### YAML Frontmatter

```yaml
---
name: using-claude-cli-wrapper
description: <one-sentence description, under 1024 chars, describing what the skill covers and when to use it>
---
```

- `name`: lowercase with hyphens only, under 64 characters
- `description`: non-empty, under 1024 characters

### Sections (in this order)

1. **Prerequisites** (~6 lines) — Claude Code CLI installed + authenticated, Python 3.10+
2. **Installation** (~8 lines) — `uv add git+https://github.com/rpakishore/claude-cli-wrapper.git`, pydantic added separately, zero runtime deps note. The package is NOT on PyPI — always install from the GitHub repo.
3. **Quick Reference** (~30 lines) — Three concise code blocks: one-shot `run()`, multi-turn `claude_session()`, Pydantic structured output
4. **`run()` Parameters** (~50 lines) — Grouped parameter tables matching the actual `run()` signature exactly. Groups: Model, System prompt, Execution, Output, Tools, Permissions, Session, Configuration, Debugging. Each table has columns: Parameter, Type, Default, Description.
5. **`ClaudeResponse`** (~18 lines) — Attributes table including `.json` and `.parsed` property behavior and when they return `None`
6. **Sessions** (~22 lines) — `claude_session()` full signature, note that `Session.run()` shares kwargs with `run()`, resume/fork examples
7. **Structured Output** (~35 lines) — JSON schema dict path (no extra deps) and Pydantic model path with code examples. Note that `response_model` auto-sets `output_format="json"`. Include a subsection on JSON schema limitations: schemas must follow the constraints at https://platform.claude.com/docs/en/build-with-claude/structured-outputs#json-schema-limitations — supported features (basic types, `enum` with primitives only, `const`, `anyOf`/`allOf`, `$ref`/`$def`/`definitions` (no external `$ref`), `default`, `required`, `additionalProperties` must be `false`, string formats `date-time`/`time`/`date`/`duration`/`email`/`hostname`/`uri`/`ipv4`/`ipv6`/`uuid`, `minItems` 0 or 1 only) and unsupported features (recursive schemas, complex enum types, external `$ref`, numerical constraints like `minimum`/`maximum`/`multipleOf`, string constraints like `minLength`/`maxLength`, array constraints beyond `minItems` 0/1, `additionalProperties` not `false`).
8. **Tool Control** (~16 lines) — `allowed_tools`, `disallowed_tools`, `tools` with code examples
9. **Custom Agents** (~16 lines) — `Agent` dataclass fields + usage example
10. **Error Handling** (~28 lines) — ASCII exception hierarchy tree showing each exception's extra attributes, then a try/except example catching all exception types
11. **Key Caveats** (~18 lines) — Numbered list of gotchas (permissions default, stdin prompts, --print flag, CLI path resolution order, cross-platform discovery, .json/.parsed None behavior, response_model constraints, keyword-only args, str enums)

### Rules

- **Accuracy over brevity**: every parameter name, type, default, and exception attribute must match the source code exactly. If a parameter was added, removed, renamed, or retyped, the SKILL.md must reflect it.
- **Under 500 lines total**.
- **No version numbers or dates** in the body (they go stale).
- **Consistent terminology**: "prompt", "response", "session", "CLI" throughout.
- **Assumes the reader knows Python** — don't explain standard library concepts. Only document what's unique to this wrapper.
- **Code examples should be minimal and runnable** — no placeholder comments, no unnecessary imports.
- **Use pipe union syntax** for types (`str | None`, not `Optional[str]`).

### Verification Checklist

After writing, verify:

- [ ] Every parameter in `run()` appears in the parameter tables with correct type and default
- [ ] Every field/property in `ClaudeResponse` appears in its table
- [ ] Every exception class appears in the hierarchy tree with correct attributes
- [ ] `Agent` dataclass fields match source
- [ ] `claude_session()` signature matches source
- [ ] YAML frontmatter: name is lowercase/hyphens, under 64 chars; description is under 1024 chars
- [ ] Total line count is under 500
