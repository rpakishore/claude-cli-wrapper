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
