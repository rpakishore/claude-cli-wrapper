"""Session management for multi-turn conversations."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

from claude_cli_wrapper.core.client import run as _run
from claude_cli_wrapper.core.response import ClaudeResponse

if TYPE_CHECKING:
    pass


class Session:
    """A session for multi-turn conversations with Claude.

    Sessions maintain conversation context across multiple prompts.
    Use the `claude_session()` context manager to create sessions.

    Attributes:
        session_id: The unique identifier for this session.

    Example:
        >>> with claude_session() as session:
        ...     r1 = session.run("What is Python?")
        ...     r2 = session.run("Give me an example")  # Remembers context
    """

    def __init__(
        self,
        session_id: str | None = None,
        resume: str | None = None,
        fork: bool = False,
        working_dir: str | Path | None = None,
        cli_path: str | None = None,
    ) -> None:
        """Initialize a session.

        Args:
            session_id: Specific session ID to use. If None, generates a new UUID.
            resume: Session ID to resume from.
            fork: If True, create a new session forked from resume.
            working_dir: Working directory for all session commands.
            cli_path: Path to Claude CLI executable.
        """
        self._resume = resume
        self._fork = fork
        self._working_dir = working_dir
        self._cli_path = cli_path
        self._first_run = True

        if resume and not fork:
            self._session_id = resume
        elif session_id:
            self._session_id = session_id
        else:
            self._session_id = str(uuid.uuid4())

    @property
    def session_id(self) -> str:
        """Get the session ID."""
        return self._session_id

    def run(
        self,
        prompt: str,
        *,
        # Model configuration
        model: str | None = None,
        fallback_model: str | None = None,
        # System prompts
        system_prompt: str | None = None,
        append_system_prompt: str | None = None,
        # Execution
        working_dir: str | Path | None = None,
        timeout: float | None = None,
        max_turns: int | None = None,
        # Output
        output_format: str | None = None,
        json_schema: dict | None = None,
        response_model: type | None = None,
        # Tools
        allowed_tools: list[str] | None = None,
        disallowed_tools: list[str] | None = None,
        tools: list[str] | None = None,
        # Permissions
        permission_mode: str | None = None,
        dangerously_skip_permissions: bool = True,
        # Configuration
        add_dirs: list[str | Path] | None = None,
        mcp_config: str | dict | None = None,
        agents: list[Any] | None = None,
        files: dict[str, str] | None = None,
        betas: list[str] | None = None,
        # Debugging
        verbose: bool = False,
    ) -> ClaudeResponse:
        """Execute a prompt within this session.

        The session context is automatically maintained across calls.

        Args:
            prompt: The prompt text to send to Claude.
            model: Model to use for this prompt.
            fallback_model: Fallback model when primary is overloaded.
            system_prompt: Replace the default system prompt.
            append_system_prompt: Append to the default system prompt.
            working_dir: Override session working directory for this call.
            timeout: Timeout in seconds for this call.
            max_turns: Maximum agentic turns for this call.
            output_format: Output format for this call.
            json_schema: JSON schema for structured output.
            response_model: Pydantic model for response parsing.
            allowed_tools: Tools to allow.
            disallowed_tools: Tools to disallow.
            tools: Restrict available tools.
            permission_mode: Permission mode.
            dangerously_skip_permissions: Skip permission checks.
            add_dirs: Additional directories.
            mcp_config: MCP configuration.
            agents: Custom agents.
            files: File resources.
            betas: Beta features.
            verbose: Enable verbose output.

        Returns:
            ClaudeResponse containing the result.
        """
        # Use session working directory if not overridden
        effective_working_dir = working_dir or self._working_dir

        # Handle session continuation
        resume = None
        fork_session = False
        use_session_id = False

        if self._first_run:
            if self._resume:
                resume = self._resume
                fork_session = self._fork
            else:
                use_session_id = True
            self._first_run = False
        else:
            # Subsequent runs continue the session
            resume = self._session_id

        response = _run(
            prompt,
            model=model,
            fallback_model=fallback_model,
            system_prompt=system_prompt,
            append_system_prompt=append_system_prompt,
            working_dir=effective_working_dir,
            timeout=timeout,
            max_turns=max_turns,
            output_format=output_format,
            json_schema=json_schema,
            response_model=response_model,
            allowed_tools=allowed_tools,
            disallowed_tools=disallowed_tools,
            tools=tools,
            permission_mode=permission_mode,
            dangerously_skip_permissions=dangerously_skip_permissions,
            session_id=self._session_id if use_session_id else None,
            resume=resume,
            fork_session=fork_session,
            cli_path=self._cli_path,
            add_dirs=add_dirs,
            mcp_config=mcp_config,
            agents=agents,
            files=files,
            betas=betas,
            verbose=verbose,
        )

        return response


@contextmanager
def claude_session(
    *,
    resume: str | None = None,
    fork: bool = False,
    working_dir: str | Path | None = None,
    cli_path: str | None = None,
) -> Generator[Session, None, None]:
    """Create a session for multi-turn conversations.

    Use this context manager to maintain conversation context across
    multiple prompts.

    Args:
        resume: Session ID to resume from a previous session.
        fork: If True and resume is provided, create a new session
            forked from the resumed session.
        working_dir: Working directory for all session commands.
        cli_path: Path to Claude CLI executable.

    Yields:
        A Session object for running prompts.

    Example:
        >>> with claude_session() as session:
        ...     r1 = session.run("What is the capital of France?")
        ...     r2 = session.run("What is its population?")
        ...     print(session.session_id)  # Save for later

        >>> # Resume a previous session
        >>> with claude_session(resume="abc-123") as session:
        ...     r = session.run("Continue our conversation")
    """
    session = Session(
        resume=resume,
        fork=fork,
        working_dir=working_dir,
        cli_path=cli_path,
    )
    yield session
