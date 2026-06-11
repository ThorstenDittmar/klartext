"""Infrastructure tests: the file-based agent mailbox (scripts/inbox.sh).

Terminal-started agent sessions are outside the desktop app's messaging fabric,
so cross-agent messages travel as files in the pinned shared memory. The mailbox
is the team's only channel once sessions migrate to terminal start — a regression
here would make agents silently unreachable, so its contract is gated by CI.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parents[3] / "scripts" / "inbox.sh"


def _run(args: list[str], base: Path, stdin: str = "") -> subprocess.CompletedProcess[str]:
    """Runs inbox.sh with an isolated mailbox base directory."""
    env = {**os.environ, "KLARTEXT_INBOX_BASE": str(base)}
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        input=stdin,
        env=env,
    )


def test_inbox_script_exists_and_is_executable() -> None:
    """Verifies scripts/inbox.sh is present and executable."""
    assert SCRIPT.exists(), "scripts/inbox.sh is missing"
    assert os.access(SCRIPT, os.X_OK), "scripts/inbox.sh is not executable"


def test_send_then_unread_count_is_one(tmp_path: Path) -> None:
    """A delivered message raises the recipient's unread count to 1."""
    send = _run(["send", "devops", "oe", "Pilot ready"], tmp_path, stdin="body text")
    assert send.returncode == 0, send.stderr
    unread = _run(["unread", "devops"], tmp_path)
    assert unread.returncode == 0, unread.stderr
    assert unread.stdout.strip() == "1"


def test_read_prints_body_then_marks_read(tmp_path: Path) -> None:
    """Reading prints the message body and drops the unread count back to 0."""
    _run(["send", "devops", "oe", "Pilot ready"], tmp_path, stdin="the body marker")
    read = _run(["read", "devops"], tmp_path)
    assert read.returncode == 0, read.stderr
    assert "the body marker" in read.stdout
    assert "Pilot ready" in read.stdout

    after = _run(["unread", "devops"], tmp_path)
    assert after.stdout.strip() == "0", "message was not marked read"
    archived = list((tmp_path / "devops" / ".read").glob("*.md"))
    assert len(archived) == 1, "read message was not archived"


def test_unread_for_empty_inbox_is_zero(tmp_path: Path) -> None:
    """An inbox that was never written reports 0 unread, not an error."""
    result = _run(["unread", "narrative"], tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "0"


def test_read_empty_inbox_is_graceful(tmp_path: Path) -> None:
    """Reading an empty inbox exits 0 with a friendly notice, not a crash."""
    result = _run(["read", "narrative"], tmp_path)
    assert result.returncode == 0, result.stderr
    assert "no unread" in result.stdout.lower()
