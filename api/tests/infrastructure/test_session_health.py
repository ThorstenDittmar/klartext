"""Infrastructure tests: the SessionStart drift-warning hook (scripts/session_health.py).

ADR-0012 detection half + the "verify current before resume" clause of the Controlled-Method-Rollout
practice: a fail-soft, NON-BLOCKING SessionStart check that warns when the worktree is behind
origin/main, pointing at `klartext converge`. It must NEVER fail or block a session — any error or
offline state → exit 0, no warning.

The detection sharpness is behind a `DriftSignal` port (L1 = commit-count) so a later L2
(shared-layer-weighted) is an adapter swap, not a rewrite.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

_SCRIPT = Path(__file__).parents[3] / "scripts" / "session_health.py"
_SETTINGS = Path(__file__).parents[3] / ".claude" / "settings.json"


def _health_sessionstart_entries() -> list[dict]:
    """Returns the SessionStart hook entries that invoke session_health.py."""
    entries = json.loads(_SETTINGS.read_text()).get("hooks", {}).get("SessionStart", [])
    return [
        e
        for e in entries
        if any("session_health.py" in h.get("command", "") for h in e.get("hooks", []))
    ]


def test_health_hook_is_wired_in_settings() -> None:
    """Expects a SessionStart hook in .claude/settings.json that runs session_health.py."""
    assert _health_sessionstart_entries(), (
        "no SessionStart entry runs session_health.py — the drift warning would never fire"
    )


def test_health_hook_matcher_is_startup_and_clear_not_compact() -> None:
    """Expects the matcher to cover startup + clear but NOT compact (git state unchanged then)."""
    matcher = _health_sessionstart_entries()[0].get("matcher", "")
    assert "startup" in matcher and "clear" in matcher, (
        "drift hook must fire on session open and /clear (when new work begins)"
    )
    assert "compact" not in matcher, (
        "drift hook should not fire on /compact — the git state does not change mid-session"
    )


def _load_module():
    """Loads scripts/session_health.py as a module so its pure functions can be unit-tested."""
    spec = importlib.util.spec_from_file_location("session_health", _SCRIPT)
    assert spec and spec.loader, f"cannot load {_SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = (
        module  # so dataclasses can resolve annotations under future-annotations
    )
    spec.loader.exec_module(module)
    return module


def _git(*args: str, cwd: Path) -> None:
    """Runs a git command in cwd with a deterministic identity."""
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _make_behind_worktree(tmp_path: Path, *, behind: int = 1) -> Path:
    """Builds an agent/devops checkout that is `behind` commits behind origin/main."""
    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--bare", "-b", "main", str(origin)], check=True, capture_output=True
    )
    work = tmp_path / "work"
    subprocess.run(["git", "clone", str(origin), str(work)], check=True, capture_output=True)
    (work / "README.md").write_text("seed\n")
    _git("add", "README.md", cwd=work)
    _git("commit", "-m", "seed", cwd=work)
    _git("push", "origin", "main", cwd=work)
    _git("checkout", "-b", "agent/devops", cwd=work)
    if behind:
        pub = tmp_path / "pub"
        subprocess.run(["git", "clone", str(origin), str(pub)], check=True, capture_output=True)
        for i in range(behind):
            (pub / f"f{i}.txt").write_text(f"{i}\n")
            _git("add", f"f{i}.txt", cwd=pub)
            _git("commit", "-m", f"advance {i}", cwd=pub)
        _git("push", "origin", "main", cwd=pub)
    return work


# --- pure DriftSignal port (L1) -------------------------------------------------


def test_commit_count_drift_warns_when_behind() -> None:
    """Expects the L1 signal to warn when the worktree is at least one commit behind."""
    m = _load_module()
    assert (
        m.CommitCountDrift().should_warn(m.DriftContext(commits_behind=2, changed_paths=())) is True
    )


def test_commit_count_drift_quiet_when_current() -> None:
    """Expects the L1 signal to stay quiet at zero commits behind."""
    m = _load_module()
    assert (
        m.CommitCountDrift().should_warn(m.DriftContext(commits_behind=0, changed_paths=()))
        is False
    )


# --- assess_drift against real repos -------------------------------------------


def test_assess_drift_warns_for_behind_worktree(tmp_path: Path) -> None:
    """Expects a behind worktree to produce a warning that points at `klartext converge`."""
    work = _make_behind_worktree(tmp_path, behind=2)
    warning = _load_module().assess_drift(work)
    assert warning is not None
    assert "converge" in warning


def test_assess_drift_quiet_for_current_worktree(tmp_path: Path) -> None:
    """Expects an up-to-date worktree to produce no warning (None)."""
    work = _make_behind_worktree(tmp_path, behind=0)
    assert _load_module().assess_drift(work) is None


def test_assess_drift_failsoft_when_offline(tmp_path: Path) -> None:
    """Expects an unreachable origin to be fail-soft: no warning, no error (never nag/ block)."""
    work = _make_behind_worktree(tmp_path, behind=1)
    _git("remote", "set-url", "origin", str(tmp_path / "gone.git"), cwd=work)
    # Must not raise and must not warn on a stale/unknown state.
    assert _load_module().assess_drift(work) is None


def test_assess_drift_failsoft_when_no_origin_remote(tmp_path: Path) -> None:
    """Expects a repo with NO origin remote to be fail-soft (fetch rc!=0 path), not just a dead URL.

    Distinct from the offline case: there the remote exists but is unreachable; here there is no
    `origin` at all, so `git fetch origin` fails to even resolve a remote.
    """
    work = tmp_path / "lonely"
    subprocess.run(
        ["git", "init", "-b", "agent/devops", str(work)], check=True, capture_output=True
    )
    (work / "README.md").write_text("seed\n")
    _git("add", "README.md", cwd=work)
    _git("commit", "-m", "seed", cwd=work)
    assert _load_module().assess_drift(work) is None


def test_assess_drift_failsoft_when_fetch_ok_but_no_origin_main(tmp_path: Path) -> None:
    """Expects fail-soft when fetch SUCCEEDS but origin/main does not exist (rev-list rc!=0 path).

    This is the only scenario that exercises the `behind.returncode != 0` guard: a repo whose
    default branch is not `main` (origin reachable, but no `origin/main` ref). Pins the contract
    that a non-`main`-default remote stays quiet rather than warning or crashing. (Note: the guard
    is belt-and-suspenders — git writes the error to stderr, so the `int(stdout or "0")` fallback
    would also yield 0/None — but this is the documented place the rev-list branch is asserted.)
    """
    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--bare", "-b", "trunk", str(origin)], check=True, capture_output=True
    )
    work = tmp_path / "work"
    subprocess.run(["git", "clone", str(origin), str(work)], check=True, capture_output=True)
    _git("checkout", "-b", "trunk", cwd=work)
    (work / "README.md").write_text("seed\n")
    _git("add", "README.md", cwd=work)
    _git("commit", "-m", "seed", cwd=work)
    _git("push", "origin", "trunk", cwd=work)
    # fetch will succeed (origin reachable) but there is no origin/main → rev-list must fail soft.
    assert _load_module().assess_drift(work) is None


def test_assess_drift_message_is_singular_at_exactly_one_behind(tmp_path: Path) -> None:
    """Expects the warning to read '1 commit behind' (singular) at exactly one commit behind."""
    work = _make_behind_worktree(tmp_path, behind=1)
    warning = _load_module().assess_drift(work)
    assert warning is not None
    assert "1 commit behind" in warning
    assert "1 commits behind" not in warning


# --- end-to-end hook behaviour (subprocess, like the identity hook) -------------


def _run_hook(project_dir: Path) -> subprocess.CompletedProcess[str]:
    """Runs session_health.py with CLAUDE_PROJECT_DIR set, as the SessionStart hook would."""
    return subprocess.run(
        [sys.executable, str(_SCRIPT)],
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
        capture_output=True,
        text=True,
    )


def test_hook_emits_sessionstart_warning_for_behind_worktree(tmp_path: Path) -> None:
    """Expects the hook to emit valid SessionStart JSON whose additionalContext warns of drift."""
    work = _make_behind_worktree(tmp_path, behind=1)
    result = _run_hook(work)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "converge" in payload["hookSpecificOutput"]["additionalContext"]


def test_hook_silent_for_current_worktree(tmp_path: Path) -> None:
    """Expects the hook to emit nothing for an up-to-date worktree (graceful, no noise)."""
    work = _make_behind_worktree(tmp_path, behind=0)
    result = _run_hook(work)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == ""


def test_hook_never_fails_on_non_git_dir(tmp_path: Path) -> None:
    """Expects the hook to exit 0 with no output in a non-git directory — never block a session."""
    result = _run_hook(tmp_path)
    assert result.returncode == 0


def test_hook_failsoft_when_git_binary_is_unavailable(tmp_path: Path) -> None:
    """Expects exit 0 with no output even when `git` is not on PATH — exercises main()'s guard.

    `assess_drift` does not wrap subprocess.run, so a missing git binary raises FileNotFoundError
    that propagates to build_warnings. The ONLY thing that stops this from crashing the session is
    the `try/except Exception -> return 0` in main(). Offline/non-git tests take the returncode
    branches and never reach that except clause; this one does. Remove main()'s guard and the hook
    exits non-zero — blocking the session, the exact contract violation this check forbids.
    """
    work = _make_behind_worktree(tmp_path, behind=1)
    result = subprocess.run(
        [sys.executable, str(_SCRIPT)],
        env={"CLAUDE_PROJECT_DIR": str(work), "PATH": "/nonexistent"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == ""


def test_hook_emits_no_stray_stdout_when_healthy(tmp_path: Path) -> None:
    """Expects byte-exact empty stdout when healthy — any stray byte would corrupt the hook JSON.

    A SessionStart hook's stdout IS the JSON contract: a stray print/log would either be parsed as
    malformed JSON or injected as bogus additionalContext. Asserts the raw stdout is empty, not just
    stripped-empty, so a lone newline or debug line is caught.
    """
    work = _make_behind_worktree(tmp_path, behind=0)
    result = _run_hook(work)
    assert result.returncode == 0, result.stderr
    assert result.stdout == "", f"unexpected stdout on healthy session: {result.stdout!r}"
    assert result.stdout.strip() == ""
