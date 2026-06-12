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


def test_send_rejects_empty_body(tmp_path: Path) -> None:
    """An empty message body is refused (non-zero exit) and nothing is written.

    An empty briefing is a silent failure — the recipient sees a heading with no
    content and does double work guessing what was meant. Fail loudly instead.
    """
    result = _run(["send", "devops", "oe", "Empty briefing"], tmp_path, stdin="")
    assert result.returncode != 0, "Expected non-zero exit for an empty body"

    unread = _run(["unread", "devops"], tmp_path)
    assert unread.stdout.strip() == "0", "an empty-body message must not be written"


def test_send_rejects_whitespace_only_body(tmp_path: Path) -> None:
    """A body consisting only of whitespace is treated as empty and refused."""
    result = _run(["send", "devops", "oe", "Blank briefing"], tmp_path, stdin="   \n\t\n")
    assert result.returncode != 0, "Expected non-zero exit for a whitespace-only body"

    unread = _run(["unread", "devops"], tmp_path)
    assert unread.stdout.strip() == "0", "a whitespace-only message must not be written"


def test_send_accepts_leading_whitespace_with_real_content(tmp_path: Path) -> None:
    r"""A body with blank leading lines but real content later is accepted, not rejected.

    The empty-body guard strips ALL whitespace to test for emptiness. It must only
    reject when nothing remains — a body like "\n\nreal text" has real content and
    must be delivered. Otherwise a legitimately indented or blank-line-prefixed
    briefing would be silently refused.
    """
    result = _run(["send", "devops", "oe", "Indented briefing"], tmp_path, stdin="\n\nreal text")
    assert result.returncode == 0, (
        f"a body with real content after blank lines must be accepted, got exit "
        f"{result.returncode}: {result.stderr}"
    )

    unread = _run(["unread", "devops"], tmp_path)
    assert unread.stdout.strip() == "1", "a body with real content must be delivered"

    read = _run(["read", "devops"], tmp_path)
    assert "real text" in read.stdout, "the real content of the body must round-trip intact"


def test_send_delivers_single_line_body_verbatim(tmp_path: Path) -> None:
    r"""A single-line body is written into the message file exactly as piped in.

    Regression guard for the cat- -> printf '%s\n' change: the body must land in
    the file verbatim, not mangled, duplicated, or truncated.
    """
    body = "the one and only body line"
    send = _run(["send", "devops", "oe", "Single line"], tmp_path, stdin=body)
    assert send.returncode == 0, send.stderr

    files = list((tmp_path / "devops").glob("*.md"))
    assert len(files) == 1, f"expected exactly one delivered file, got {files}"
    content = files[0].read_text()
    assert content.count(body) == 1, f"body must appear exactly once, file was:\n{content}"
    assert content.endswith(body + "\n"), (
        f"body must be the final line terminated by a single newline, file was:\n{content!r}"
    )


def test_send_preserves_multiline_body_intact(tmp_path: Path) -> None:
    r"""A multi-line body (including an internal blank line) round-trips line for line.

    cat- via command substitution strips trailing newlines; the script re-adds one
    via printf '%s\n'. A multi-line body with an internal blank line must survive
    intact — every line present, in order, none collapsed.
    """
    body = "first line\nsecond line\n\nfourth line after a blank"
    send = _run(["send", "devops", "oe", "Multi line"], tmp_path, stdin=body)
    assert send.returncode == 0, send.stderr

    files = list((tmp_path / "devops").glob("*.md"))
    assert len(files) == 1, f"expected exactly one delivered file, got {files}"
    content = files[0].read_text()
    for line in ("first line", "second line", "fourth line after a blank"):
        assert line in content, f"line {line!r} missing from delivered file:\n{content}"
    assert body + "\n" in content, (
        f"the full multi-line body must appear contiguous and intact, file was:\n{content!r}"
    )

    read = _run(["read", "devops"], tmp_path)
    assert body in read.stdout, f"read must print the full multi-line body, got:\n{read.stdout!r}"


def test_send_preserves_leading_and_trailing_spaces_within_content(tmp_path: Path) -> None:
    """Leading and trailing spaces on a content line are preserved, not trimmed.

    The guard strips whitespace only to decide emptiness — it must not actually
    mutate the stored body. A body with meaningful indentation must be stored as-is.
    """
    body = "   indented content with trailing spaces   "
    send = _run(["send", "devops", "oe", "Spacing"], tmp_path, stdin=body)
    assert send.returncode == 0, send.stderr

    files = list((tmp_path / "devops").glob("*.md"))
    assert len(files) == 1, f"expected exactly one delivered file, got {files}"
    content = files[0].read_text()
    assert body + "\n" in content, (
        f"leading/trailing spaces within the content line must be preserved, file was:\n{content!r}"
    )


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
