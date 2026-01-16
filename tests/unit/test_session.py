"""Unit tests for session management."""

from unittest.mock import MagicMock, patch

from claude_cli_wrapper.core.session import Session, claude_session


def mock_run_response(**kwargs):
    """Create a mock ClaudeResponse."""
    mock = MagicMock()
    mock.text = kwargs.get("text", "response")
    mock.exit_code = kwargs.get("exit_code", 0)
    mock.stderr = kwargs.get("stderr", "")
    mock.command = kwargs.get("command", ["claude"])
    mock.working_dir = kwargs.get("working_dir", "/tmp")
    mock.duration = kwargs.get("duration", 1.0)
    return mock


class TestSession:
    """Tests for Session class."""

    def test_generates_session_id(self) -> None:
        """Session should generate a UUID if none provided."""
        session = Session()
        assert session.session_id is not None
        assert len(session.session_id) > 0

    def test_uses_provided_session_id(self) -> None:
        """Session should use provided session_id."""
        session = Session(session_id="my-custom-id")
        assert session.session_id == "my-custom-id"

    def test_uses_resume_as_session_id(self) -> None:
        """Session should use resume ID as session_id when not forking."""
        session = Session(resume="resumed-session")
        assert session.session_id == "resumed-session"

    def test_generates_new_id_when_forking(self) -> None:
        """Session should generate new ID when forking."""
        session = Session(resume="original-session", fork=True)
        assert session.session_id != "original-session"

    @patch("claude_cli_wrapper.core.session._run")
    def test_run_calls_underlying_run(self, mock_run) -> None:
        """Session.run should call the underlying run function."""
        mock_run.return_value = mock_run_response()
        session = Session()

        session.run("Test prompt")

        mock_run.assert_called_once()
        assert mock_run.call_args.args[0] == "Test prompt"

    @patch("claude_cli_wrapper.core.session._run")
    def test_first_run_uses_session_id(self, mock_run) -> None:
        """First run should use session_id parameter."""
        mock_run.return_value = mock_run_response()
        session = Session(session_id="test-session")

        session.run("First prompt")

        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["session_id"] == "test-session"

    @patch("claude_cli_wrapper.core.session._run")
    def test_subsequent_runs_use_resume(self, mock_run) -> None:
        """Subsequent runs should use resume with session_id."""
        mock_run.return_value = mock_run_response()
        session = Session(session_id="test-session")

        session.run("First prompt")
        session.run("Second prompt")

        # Second call should use resume
        second_call_kwargs = mock_run.call_args.kwargs
        assert second_call_kwargs["resume"] == "test-session"

    @patch("claude_cli_wrapper.core.session._run")
    def test_uses_session_working_dir(self, mock_run) -> None:
        """Session should use its working_dir for all runs."""
        mock_run.return_value = mock_run_response()
        session = Session(working_dir="/session/dir")

        session.run("Test")

        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["working_dir"] == "/session/dir"

    @patch("claude_cli_wrapper.core.session._run")
    def test_run_can_override_working_dir(self, mock_run) -> None:
        """Session.run should allow overriding working_dir."""
        mock_run.return_value = mock_run_response()
        session = Session(working_dir="/session/dir")

        session.run("Test", working_dir="/override/dir")

        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["working_dir"] == "/override/dir"


class TestClaudeSessionContextManager:
    """Tests for claude_session context manager."""

    def test_yields_session(self) -> None:
        """claude_session should yield a Session object."""
        with claude_session() as session:
            assert isinstance(session, Session)

    def test_passes_resume_to_session(self) -> None:
        """claude_session should pass resume to Session."""
        with claude_session(resume="abc-123") as session:
            assert session.session_id == "abc-123"

    def test_passes_fork_to_session(self) -> None:
        """claude_session should pass fork to Session."""
        with claude_session(resume="abc-123", fork=True) as session:
            assert session.session_id != "abc-123"

    def test_passes_working_dir_to_session(self) -> None:
        """claude_session should pass working_dir to Session."""
        with claude_session(working_dir="/test/dir") as session:
            assert session._working_dir == "/test/dir"

    def test_passes_cli_path_to_session(self) -> None:
        """claude_session should pass cli_path to Session."""
        with claude_session(cli_path="/custom/claude") as session:
            assert session._cli_path == "/custom/claude"


class TestSessionMultiTurn:
    """Tests for multi-turn conversation behavior."""

    @patch("claude_cli_wrapper.core.session._run")
    def test_first_run_with_resume_passes_resume(self, mock_run) -> None:
        """First run with resume should pass resume parameter."""
        mock_run.return_value = mock_run_response()

        with claude_session(resume="old-session") as session:
            session.run("Continue")

        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["resume"] == "old-session"

    @patch("claude_cli_wrapper.core.session._run")
    def test_first_run_with_fork_passes_fork_session(self, mock_run) -> None:
        """First run with fork should pass fork_session=True."""
        mock_run.return_value = mock_run_response()

        with claude_session(resume="old-session", fork=True) as session:
            session.run("Fork and continue")

        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["resume"] == "old-session"
        assert call_kwargs["fork_session"] is True
