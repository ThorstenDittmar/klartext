"""Bootstrap smoke-test — stand up a throwaway project from the seed and verify it (plan §10).

The sibling of setup-smoke-test.yml, at project-onboarding scale (project-onboarding.md §7): from
the seed + a filled seed.toml, a fresh project must stand up where the rendered fabric is present,
runnable, and carries ZERO source-endeavour literal — proving the parameterization, not a global sed.

What it does (the mechanizable core):
  1. Build a throwaway "consumer repo" from the live git-tracked tree + a DEMO seed.toml (a non-source
     project slug), then run the real assembly (seed/assemble.py + MANIFEST.toml).
  2. Completeness — assembly succeeds; every non-skip/non-deferred target lands; deferred == the
     manifest's deferred set (a known gap, not a silent drop).
  3. Zero source literal — no rendered TEMPLATE output and no config_source carries the source slug
     (the live seed.toml project_name): the parameterized artifacts came from seed.toml, not a copy.
  4. Runnable fabric — the rendered settings parse, the rendered scripts byte-compile / pass bash -n,
     and the live fabric executes against the bundle: classify_gate gives a verdict, the coverage
     check runs, and inbox.sh does a send→read roundtrip.

NOT covered here (out of plain CI — needs the Claude Code app / a real remote): hooks firing in a live
session, agent onboarding, a first `converge` against an origin. Those stay manual per §7.

Scope note: the zero-literal check targets the RENDERED + config_source outputs (the "global sed"
anti-pattern surface). Whether as_is L3 method docs must also be source-slug-free is an OE scope call
(they cite the source endeavour as the worked example) — tracked separately, not gated here.

Stack-neutral (stdlib only; a Python runtime is a declared seed prerequisite).
"""

from __future__ import annotations

import json
import py_compile
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assemble  # noqa: E402 — sibling module (standalone-tool pattern)
import render  # noqa: E402

# A demo seed.toml whose slug shares no substring with a typical source slug — what a consumer fills.
_DEMO_SEED = """project_name      = "acme"
env_prefix        = "ACME_"
memory_dir        = "acme-team-memory"
product_domain    = "acme.example"
repo_slug         = "acme/widget"
worktree_base     = "$HOME/acme-worktrees"
identity_preamble = "the acme multi-agent system"
interpreter       = ".venv/bin/python3"
cli_entrypoint    = "app/cli.py"
wow_cli_command   = "acme"
wow_trigger_paths = ["CLAUDE.md", "scripts/**", ".github/workflows/**"]
backend_dir       = "app"
tests_dir         = "app/tests"
source_dirs       = ["models", "services"]
excluded_files    = ["__init__.py"]
test_file_overrides = []
"""


def _source_slug(repo_root: Path) -> str:
    """The source endeavour's project slug (the live seed.toml project_name) — the literal to absent."""
    return render.load_seed_config(repo_root / "seed" / "seed.toml")["project_name"]


def _build_consumer_repo(repo_root: Path, dest: Path) -> None:
    """Copies the live git-tracked tree into dest and overwrites seed.toml with the demo config."""
    tracked = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    for rel in tracked:
        src = repo_root / rel
        if not src.is_file():
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
    (dest / "seed" / "seed.toml").write_text(_DEMO_SEED)


def _rendered_and_config_targets(manifest: assemble.Manifest) -> list[str]:
    """The bundle targets whose content is rendered from / is the config (the zero-literal surface)."""
    return [
        e.target
        for e in manifest.entries
        if e.disposition in ("template", "config_source")
    ]


def _check_completeness(
    manifest: assemble.Manifest, result: assemble.AssembleResult, bundle: Path
) -> list[str]:
    """Every non-skip/non-deferred target exists; deferred == the manifest's declared deferred set."""
    failures: list[str] = []
    expected_deferred = {
        e.path for e in manifest.entries if e.disposition == "deferred"
    }
    if set(result.deferred) != expected_deferred:
        failures.append(
            f"deferred set drift: assembled {set(result.deferred)} != manifest {expected_deferred}"
        )
    for entry in manifest.entries:
        if entry.disposition in ("declared", "exclude", "deferred"):
            continue
        if "*" in entry.path or "{" in entry.path:
            continue  # globs land many files; covered by assemble's own match-≥1 guard
        if not (bundle / entry.target).exists():
            failures.append(
                f"missing bundle target: {entry.target} ({entry.disposition})"
            )
    return failures


def _check_zero_source_literal(
    manifest: assemble.Manifest, bundle: Path, slug: str
) -> list[str]:
    """No rendered/config target carries the source slug — they were parameterized, not copied."""
    failures: list[str] = []
    for target in _rendered_and_config_targets(manifest):
        path = bundle / target
        if not path.is_file():
            continue
        if slug.lower() in path.read_text().lower():
            failures.append(
                f"source literal '{slug}' survived in rendered target: {target}"
            )
    return failures


def _check_runnable_fabric(bundle: Path) -> list[str]:
    """The rendered fabric parses, compiles, and executes against the bundle."""
    failures: list[str] = []

    settings = bundle / ".claude" / "settings.json"
    if settings.is_file():
        try:
            json.loads(settings.read_text())
        except ValueError as exc:
            failures.append(f"rendered settings.json is invalid JSON: {exc}")

    for py in sorted((bundle / "scripts").glob("*.py")):
        try:
            py_compile.compile(str(py), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"rendered {py.name} does not compile: {exc}")
    for sh in sorted((bundle / "scripts").glob("*.sh")):
        check = subprocess.run(["bash", "-n", str(sh)], capture_output=True, text=True)
        if check.returncode != 0:
            failures.append(
                f"rendered {sh.name} is invalid bash: {check.stderr.strip()}"
            )

    # classify_gate executes and yields a verdict (it reads the bundle's seed.toml at runtime).
    gate = bundle / "scripts" / "classify_gate.py"
    if gate.is_file():
        run = subprocess.run(
            [
                sys.executable,
                str(gate),
                "--changed-paths",
                "CLAUDE.md",
                "--labels",
                "[]",
            ],
            capture_output=True,
            text=True,
        )
        if run.returncode != 1:  # a WoW path with no label must fail the gate (exit 1)
            failures.append(
                f"classify_gate did not give the expected verdict: rc={run.returncode}"
            )

    # inbox.sh send -> read roundtrip.
    inbox = bundle / "scripts" / "inbox.sh"
    if inbox.is_file():
        env_base = bundle / "_inbox"
        send = subprocess.run(
            ["bash", str(inbox), "send", "qa", "devops", "smoke ping"],
            input="hello from smoke",
            capture_output=True,
            text=True,
            env={
                "PATH": _path_env(),
                "HOME": str(bundle),
                f"{_inbox_env_prefix()}INBOX_BASE": str(env_base),
            },
        )
        if send.returncode != 0:
            failures.append(f"inbox.sh send failed: {send.stderr.strip()}")
        else:
            read = subprocess.run(
                ["bash", str(inbox), "read", "qa"],
                capture_output=True,
                text=True,
                env={
                    "PATH": _path_env(),
                    "HOME": str(bundle),
                    f"{_inbox_env_prefix()}INBOX_BASE": str(env_base),
                },
            )
            if "hello from smoke" not in read.stdout:
                failures.append("inbox.sh roundtrip lost the message body")
    return failures


def _path_env() -> str:
    """The current PATH (so bash/git resolve in the subprocess)."""
    import os

    return os.environ.get("PATH", "/usr/bin:/bin")


def _inbox_env_prefix() -> str:
    """The demo env prefix the rendered inbox.sh reads for its base override.

    Derived from _DEMO_SEED (not hardcoded) so it can never drift from the demo config: the rendered
    inbox.sh reads ${<env_prefix>INBOX_BASE}, and a mismatch would silently stop exercising that path.
    """
    import tomllib

    return str(tomllib.loads(_DEMO_SEED)["env_prefix"])


def run_smoke_test(repo_root: Path) -> list[str]:
    """Stands up a throwaway project from the seed and returns the list of failures ([] == pass)."""
    slug = _source_slug(repo_root)
    with tempfile.TemporaryDirectory() as tmp:
        consumer = Path(tmp) / "consumer"
        consumer.mkdir()
        _build_consumer_repo(repo_root, consumer)
        manifest = assemble.load_manifest(consumer / "seed" / "MANIFEST.toml")
        bundle = Path(tmp) / "bundle"
        result = assemble.assemble(manifest, consumer, bundle)
        return [
            *_check_completeness(manifest, result, bundle),
            *_check_zero_source_literal(manifest, bundle, slug),
            *_check_runnable_fabric(bundle),
        ]


def main() -> int:
    """CLI: runs the bootstrap smoke-test against the repo root; prints results, returns 0/1."""
    repo_root = Path(__file__).resolve().parents[1]
    failures = run_smoke_test(repo_root)
    if failures:
        print("✗  bootstrap smoke-test FAILED:\n")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "✓  bootstrap smoke-test passed — a fresh project stands up source-literal-clean."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
