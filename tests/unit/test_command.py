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
        files = {"file_abc": "doc.pdf", "file_def": "img.png"}
        cmd = build_command("claude", files=files)
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
