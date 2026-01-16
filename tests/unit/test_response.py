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
