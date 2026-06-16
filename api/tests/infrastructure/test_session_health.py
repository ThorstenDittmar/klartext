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


# --- memory-substrate checks: C1 (pin resolves) + C3 (inbox reachable) ----------


def _make_klartext_dir(
    tmp_path: Path, *, pin: str | None = "~/.claude/klartext-team-memory", with_inbox: bool = True
) -> Path:
    """Builds a klartext-worktree-like dir: .claude/settings.json + optional scripts/inbox.sh.

    The .claude/ dir marks it as an agent worktree; the memory-substrate checks apply only there
    (a bare directory is not a finding). `pin=None` writes settings.json without the pin key.
    """
    d = tmp_path / "wt"
    (d / ".claude").mkdir(parents=True)
    data: dict = {}
    if pin is not None:
        data["autoMemoryDirectory"] = pin
    (d / ".claude" / "settings.json").write_text(json.dumps(data))
    if with_inbox:
        (d / "scripts").mkdir()
        (d / "scripts" / "inbox.sh").write_text("#!/usr/bin/env bash\n")
    return d


def test_check_pin_none_for_non_klartext_dir(tmp_path: Path) -> None:
    """Expects no finding for a plain dir without .claude/ — it is not an agent worktree."""
    assert _load_module().check_pin(tmp_path) is None


def test_check_pin_passes_for_correct_pin(tmp_path: Path) -> None:
    """Expects no finding when autoMemoryDirectory resolves to the expected team path (C1)."""
    expected = tmp_path / "team-memory"
    d = _make_klartext_dir(tmp_path, pin=str(expected))
    assert _load_module().check_pin(d, expected_dir=expected) is None


def test_check_pin_warns_for_wrong_pin(tmp_path: Path) -> None:
    """Expects a finding when the pin does not resolve to the shared team path (C1 violated)."""
    d = _make_klartext_dir(tmp_path, pin="/somewhere/else")
    warning = _load_module().check_pin(d, expected_dir=tmp_path / "team-memory")
    assert warning is not None
    assert "autoMemoryDirectory" in warning


def test_check_pin_warns_when_pin_absent(tmp_path: Path) -> None:
    """Expects a finding when an agent worktree's settings.json carries no autoMemoryDirectory."""
    d = _make_klartext_dir(tmp_path, pin=None)
    assert _load_module().check_pin(d, expected_dir=tmp_path / "team-memory") is not None


def test_check_inbox_none_for_non_klartext_dir(tmp_path: Path) -> None:
    """Expects no finding for a plain dir without .claude/ — not an agent worktree."""
    assert _load_module().check_inbox(tmp_path) is None


def test_check_inbox_passes_when_script_present(tmp_path: Path) -> None:
    """Expects no finding when scripts/inbox.sh is reachable from the worktree (C3)."""
    d = _make_klartext_dir(tmp_path, with_inbox=True)
    assert _load_module().check_inbox(d) is None


def test_check_inbox_warns_when_script_missing(tmp_path: Path) -> None:
    """Expects a finding when scripts/inbox.sh is missing — the cross-agent inbox is unreachable."""
    d = _make_klartext_dir(tmp_path, with_inbox=False)
    warning = _load_module().check_inbox(d)
    assert warning is not None
    assert "inbox" in warning.lower()


def test_build_warnings_aggregates_pin_finding(tmp_path: Path) -> None:
    """Expects build_warnings to include a memory-substrate finding (here: a wrong pin)."""
    d = _make_klartext_dir(tmp_path, pin="/wrong/path")  # never equals the real default team path
    warning = _load_module().build_warnings(d)
    assert warning is not None
    assert "autoMemoryDirectory" in warning


# --- QA gap-fill: tilde resolution, malformed settings, fail-soft, multi-finding ---


def test_check_pin_passes_for_tilde_pin_against_default_team_dir(tmp_path: Path) -> None:
    """Expects the PRODUCTION tilde pin to resolve against _team_memory_dir() — no finding.

    The committed pin in .claude/settings.json is the tilde form `~/.claude/klartext-team-memory`,
    and the default expected path comes from _team_memory_dir() (Path.home()/.claude/...). Every
    other C1 test passes an ABSOLUTE expected_dir, so none of them exercise the tilde-expand +
    _team_memory_dir() agreement that the live hook actually depends on. If _team_memory_dir()
    stopped expanding ~ (or os.path.expanduser were dropped from check_pin), this test catches it
    while production would otherwise warn on every healthy session.
    """
    m = _load_module()
    d = _make_klartext_dir(tmp_path, pin="~/.claude/klartext-team-memory")
    # No expected_dir → check_pin uses _team_memory_dir(); both sides must resolve to home-expanded.
    assert m.check_pin(d) is None, (
        "production tilde pin must resolve against _team_memory_dir() — drift here means the live "
        "hook warns on a correctly-pinned worktree"
    )


def test_check_pin_warns_on_malformed_settings_json(tmp_path: Path) -> None:
    """Expects the except (OSError/ValueError) branch on malformed JSON — a finding, not a crash.

    `.claude/` present but settings.json is invalid JSON — the json.loads failure branch. Without
    this test that branch is untested and a refactor could let the JSONDecodeError escape.
    """
    m = _load_module()
    d = tmp_path / "wt"
    (d / ".claude").mkdir(parents=True)
    (d / ".claude" / "settings.json").write_text("{ this is not json")
    warning = m.check_pin(d, expected_dir=tmp_path / "team-memory")
    assert warning is not None
    assert "settings.json" in warning


def test_check_pin_warns_when_settings_json_missing(tmp_path: Path) -> None:
    """Expects the OSError branch to fire when .claude/ exists but settings.json is absent.

    Agent worktree (.claude/ present) with no settings.json → read_text raises OSError, which the
    except must catch and turn into a finding rather than let it propagate to build_warnings.
    """
    m = _load_module()
    d = tmp_path / "wt"
    (d / ".claude").mkdir(parents=True)
    warning = m.check_pin(d, expected_dir=tmp_path / "team-memory")
    assert warning is not None
    assert "settings.json" in warning


def test_build_warnings_aggregates_pin_and_inbox_together(tmp_path: Path) -> None:
    """Expects BOTH C1 and C3 findings to combine into one newline-joined block (multi-finding).

    Only the single-finding aggregation is covered above. This asserts that when the pin is wrong
    AND inbox.sh is missing, build_warnings returns one string containing both — newline-joined,
    not silently dropping one. Guards the newline-join path with more than one part.
    """
    m = _load_module()
    d = _make_klartext_dir(tmp_path, pin="/wrong/path", with_inbox=False)
    warning = m.build_warnings(d)
    assert warning is not None
    assert "autoMemoryDirectory" in warning
    assert "inbox" in warning.lower()
    assert "\n" in warning, "two findings must be joined, not collapsed to one"


def test_hook_stays_exit_zero_when_substrate_finding_present(tmp_path: Path) -> None:
    """Expects the e2e hook to exit 0 and emit valid JSON when a C1 finding fires (not just drift).

    The pure check tests prove check_pin returns a string; this proves the full hook path — through
    build_warnings, main(), json.dump — survives a substrate-only finding (no git drift) and still
    produces a parseable SessionStart payload. A substrate finding must never block or corrupt.
    """
    d = _make_klartext_dir(tmp_path, pin="/wrong/path")
    # Sanity: this dir is not a git repo, so drift is None — the finding is C1 only.
    result = _run_hook(d)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "autoMemoryDirectory" in payload["hookSpecificOutput"]["additionalContext"]


# --- Memory-substrate C2: durable substrate (the team memory exists and is writable) ---


def test_check_durable_passes_when_memory_dir_exists_and_writable(tmp_path: Path) -> None:
    """Expects no C2 finding when the team-memory dir exists and is writable."""
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    mem = tmp_path / "team-memory"
    mem.mkdir()
    assert m.check_durable(d, memory_dir=mem) is None


def test_check_durable_warns_when_memory_dir_missing(tmp_path: Path) -> None:
    """Expects a C2 finding when the team-memory dir does not exist (False-Persistence class)."""
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    warning = m.check_durable(d, memory_dir=tmp_path / "absent")
    assert warning is not None and "C2" in warning


def test_check_durable_warns_when_memory_dir_not_writable(tmp_path: Path) -> None:
    """Expects a C2 finding when the team-memory dir exists but is read-only.

    Durability means writable: a read-only substrate cannot persist knowledge meant to
    outlive the session. chmod 0o500 removes write; restored in finally so tmp cleanup works.
    """
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    mem = tmp_path / "ro"
    mem.mkdir()
    mem.chmod(0o500)
    try:
        warning = m.check_durable(d, memory_dir=mem)
    finally:
        mem.chmod(0o700)
    assert warning is not None and "C2" in warning


def test_check_durable_noops_outside_agent_worktree(tmp_path: Path) -> None:
    """Expects no C2 finding for a bare directory (no .claude/) — the check is worktree-gated."""
    m = _load_module()
    assert m.check_durable(tmp_path, memory_dir=tmp_path / "absent") is None


# --- Memory-substrate C4: MEMORY.md index integrity (every entry -> a real file, no duplicates) ---


def test_check_index_integrity_passes_for_consistent_index(tmp_path: Path) -> None:
    """Expects no C4 finding when every MEMORY.md entry points at an existing file."""
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    mem = tmp_path / "team-memory"
    mem.mkdir()
    (mem / "foo.md").write_text("x")
    (mem / "MEMORY.md").write_text("# Memory Index\n\n- [Foo](foo.md) — a hook\n")
    assert m.check_index_integrity(d, memory_dir=mem) is None


def test_check_index_integrity_warns_on_missing_target(tmp_path: Path) -> None:
    """Expects a C4 finding naming the missing file when an entry points at a non-existent file."""
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    mem = tmp_path / "team-memory"
    mem.mkdir()
    (mem / "MEMORY.md").write_text("- [Ghost](ghost.md) — gone\n")
    warning = m.check_index_integrity(d, memory_dir=mem)
    assert warning is not None and "ghost.md" in warning and "C4" in warning


def test_check_index_integrity_warns_on_duplicate_entry(tmp_path: Path) -> None:
    """Expects a C4 finding when the same target appears twice in the index (clobber signal)."""
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    mem = tmp_path / "team-memory"
    mem.mkdir()
    (mem / "a.md").write_text("x")
    (mem / "MEMORY.md").write_text("- [A](a.md) — one\n- [A again](a.md) — two\n")
    warning = m.check_index_integrity(d, memory_dir=mem)
    assert warning is not None and "duplicate" in warning.lower()


def test_check_index_integrity_noops_when_no_index(tmp_path: Path) -> None:
    """Expects no C4 finding when MEMORY.md does not exist yet (nothing to verify)."""
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    mem = tmp_path / "team-memory"
    mem.mkdir()
    assert m.check_index_integrity(d, memory_dir=mem) is None


def test_check_index_integrity_ignores_external_http_links(tmp_path: Path) -> None:
    """Expects http(s) links in the index to be ignored — they are not local memory files."""
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    mem = tmp_path / "team-memory"
    mem.mkdir()
    (mem / "MEMORY.md").write_text("- [A PR](https://github.com/x/y/pull/1) — external\n")
    assert m.check_index_integrity(d, memory_dir=mem) is None


# --- QA gap-fill: C2 file-not-dir; C4 subpath / both-problems / wikilink / mixed / empty;
#     build_warnings integration of the two new checks; e2e JSON for a C2/C4-only finding ---


def test_check_durable_warns_when_memory_path_is_a_file_not_dir(tmp_path: Path) -> None:
    """Expects a C2 finding when the memory path exists but is a FILE, not a directory.

    `check_durable` gates on `is_dir()`, so a regular file at the memory path is the same
    failure class as a missing dir — the substrate cannot hold the memory tree. No existing
    test exercises the exists-but-not-a-dir case (the missing case uses an absent path).
    """
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    mem = tmp_path / "memfile"
    mem.write_text("not a directory")
    warning = m.check_durable(d, memory_dir=mem)
    assert warning is not None and "C2" in warning


def test_check_index_integrity_resolves_subpath_link_target(tmp_path: Path) -> None:
    """Expects a nested link target `](sub/dir/foo.md)` to resolve relative to the memory dir.

    The capture regex grabs the whole subpath and `(mem / t).is_file()` must join it correctly.
    Existing tests only use flat targets, so the regex/path-join agreement for nested targets is
    unverified — if either drifted, a valid nested entry would be flagged as missing (false C4).
    """
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    mem = tmp_path / "team-memory"
    mem.mkdir()
    (mem / "sub" / "dir").mkdir(parents=True)
    (mem / "sub" / "dir" / "foo.md").write_text("x")
    (mem / "MEMORY.md").write_text("- [Foo](sub/dir/foo.md) — nested\n")
    assert m.check_index_integrity(d, memory_dir=mem) is None


def test_check_index_integrity_reports_both_missing_and_duplicate(tmp_path: Path) -> None:
    """Expects a single C4 finding to name BOTH a missing target and a duplicate target.

    Exercises the multi-problem `" ".join(problems)` path: one entry points at a non-existent
    file while a different target appears twice. Existing tests only ever trigger one problem at
    a time, so a regression that dropped one branch's message would go unnoticed.
    """
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    mem = tmp_path / "team-memory"
    mem.mkdir()
    (mem / "dup.md").write_text("x")
    (mem / "MEMORY.md").write_text(
        "- [Ghost](ghost.md) — missing\n- [Dup](dup.md) — one\n- [Dup again](dup.md) — two\n"
    )
    warning = m.check_index_integrity(d, memory_dir=mem)
    assert warning is not None
    assert "ghost.md" in warning
    assert "dup.md" in warning
    assert "missing" in warning.lower() and "duplicate" in warning.lower()


def test_check_index_integrity_ignores_wikilinks(tmp_path: Path) -> None:
    """Expects `[[wikilink]]` syntax to be ignored — it is not a markdown `](...)` link.

    A wikilink has no `](...)` form, so the capture regex must not pick it up; otherwise a
    wikilink would be treated as a (missing) local file and produce a false C4 finding.
    """
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    mem = tmp_path / "team-memory"
    mem.mkdir()
    (mem / "MEMORY.md").write_text("- See [[some-wikilink-note]] for context\n")
    assert m.check_index_integrity(d, memory_dir=mem) is None


def test_check_index_integrity_checks_local_when_mixed_with_http(tmp_path: Path) -> None:
    """Expects local targets to still be verified when an http link sits in the same file.

    The http-only test proves external links are skipped; this proves the filtering does not
    also drop the local entry beside it — a missing local file in a mixed index must still warn.
    """
    m = _load_module()
    d = _make_klartext_dir(tmp_path)
    mem = tmp_path / "team-memory"
    mem.mkdir()
    (mem / "MEMORY.md").write_text(
        "- [A PR](https://github.com/x/y/pull/1) — external\n- [Local](missing-local.md) — gone\n"
    )
    warning = m.check_index_integrity(d, memory_dir=mem)
    assert warning is not None
    assert "missing-local.md" in warning
    assert "github.com" not in warning


def test_build_warnings_includes_durable_finding(tmp_path: Path, monkeypatch) -> None:
    """Expects build_warnings to surface a C2 finding — proves check_durable is actually wired in.

    The pure check tests prove check_durable returns a string, but build_warnings calls it with no
    injectable memory dir. Monkeypatching `_team_memory_dir` to an absent path makes the C2 check
    fire deterministically, asserting it is part of the aggregate and not an unreferenced function.
    Pin is correct and there is no git repo, so C2 is the only substrate finding.
    """
    m = _load_module()
    absent = tmp_path / "absent-team-memory"
    d = _make_klartext_dir(tmp_path, pin=str(absent))
    monkeypatch.setattr(m, "_team_memory_dir", lambda: absent)
    warning = m.build_warnings(d)
    assert warning is not None
    assert "C2" in warning


def test_build_warnings_includes_index_integrity_finding(tmp_path: Path, monkeypatch) -> None:
    """Expects build_warnings to surface a C4 finding — proves check_index_integrity is wired in.

    Monkeypatches `_team_memory_dir` to a dir with a broken MEMORY.md so the C4 check fires through
    the aggregate. Pin is correct and the dir exists+writable (no C2), so the C4 line is isolated —
    proving build_warnings invokes check_index_integrity, not just the pure function in isolation.
    """
    m = _load_module()
    mem = tmp_path / "team-memory"
    mem.mkdir()
    (mem / "MEMORY.md").write_text("- [Ghost](ghost.md) — gone\n")
    d = _make_klartext_dir(tmp_path, pin=str(mem))
    monkeypatch.setattr(m, "_team_memory_dir", lambda: mem)
    warning = m.build_warnings(d)
    assert warning is not None
    assert "C4" in warning


def test_main_emits_valid_json_when_index_finding_is_only_finding(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """Expects main() to exit 0 with valid SessionStart JSON when a C4 finding is the ONLY finding.

    Existing e2e coverage only drives a C1 (pin) finding through main()->json.dump. This drives a
    C4-only finding (correct pin, no git drift, broken index) through the full main() path and
    asserts the payload still parses and carries the C4 text — proving a C4 finding neither blocks
    nor corrupts the hook output. The team-memory dir is injected via monkeypatching
    `_team_memory_dir` because build_warnings/main give no env hook for it (a real subprocess would
    have to write into the developer's actual ~/.claude — not acceptable in a test).
    """
    m = _load_module()
    expected = tmp_path / "team-memory"
    expected.mkdir()
    (expected / "MEMORY.md").write_text("- [Ghost](ghost.md) — gone\n")
    d = _make_klartext_dir(tmp_path, pin=str(expected))
    monkeypatch.setattr(m, "_team_memory_dir", lambda: expected)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(d))
    rc = m.main()
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "C4" in payload["hookSpecificOutput"]["additionalContext"]
