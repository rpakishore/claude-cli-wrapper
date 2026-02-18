"""Response object for Claude CLI output."""

from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


_METADATA_KEYS = (
    "session_id",
    "total_cost_usd",
    "usage",
    "num_turns",
    "duration_ms",
    "duration_api_ms",
    "is_error",
    "stop_reason",
    "subtype",
)


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
        metadata: CLI envelope metadata (session_id, cost, usage, etc.)
            when ``output_format="json"`` was used.  ``None`` otherwise.

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
    _cli_envelope: dict | None = field(default=None, repr=False)
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
    def metadata(self) -> dict | None:
        """Return CLI envelope metadata when available.

        When ``output_format="json"`` is used, the CLI wraps the model's
        response in a metadata envelope containing session information,
        cost, usage statistics, etc.  This property returns the useful
        subset of those fields.

        Returns:
            A dict with keys like ``session_id``, ``total_cost_usd``,
            ``usage``, ``num_turns``, ``duration_ms``, ``is_error``, etc.
            Returns ``None`` if no envelope was captured.
        """
        if self._cli_envelope is None:
            return None
        return {
            k: self._cli_envelope[k] for k in _METADATA_KEYS if k in self._cli_envelope
        }

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
            # Prefer structured_output from CLI envelope when available
            if (
                self._cli_envelope is not None
                and "structured_output" in self._cli_envelope
            ):
                so = self._cli_envelope["structured_output"]
                if isinstance(so, dict):
                    self._parsed_json = so
                elif isinstance(so, str):
                    with contextlib.suppress(json.JSONDecodeError):
                        self._parsed_json = json.loads(so)

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
                from pydantic import BaseModel  # noqa: F401
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
