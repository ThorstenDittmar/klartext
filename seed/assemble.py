"""Method-seed bundle assembly (Model B — OE bundling decision, user-ratified 2026-06-19).

seed/ stores only the seed-specific `.tmpl` files + this assembly mechanism (+ OE's MANIFEST, the
authoritative list of what is rendered vs pulled as-is). `assemble` produces a self-contained bundle
on demand: it renders each template from `seed.toml` and copies each as-is file VERBATIM from the live
repo. No as-is file is stored in seed/ — the single source of truth stays the live repo; the bundle is
the self-contained artefact. Stack-neutral (stdlib only; a Python runtime is a declared prerequisite).

The manifest format here is a simple interim TOML (`[[template]]` / `[[as_is]]` with `src`/`dest`);
OE defines the authoritative format, and this loader is the seam to adapt when it lands.
"""

from __future__ import annotations

import shutil
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402 — sibling module; seed/ is on the path above (standalone-tool pattern)


class AssemblyError(Exception):
    """Raised when a manifest source is missing — the bundle must be complete, never silently partial."""


@dataclass(frozen=True)
class Manifest:
    """What the bundle contains: templates to render and as-is files to copy, each as (src, dest)."""

    templates: list[tuple[str, str]]
    as_is: list[tuple[str, str]]


def load_manifest(path: Path) -> Manifest:
    """Parses the interim TOML manifest into (src, dest) pairs for templates and as-is files.

    Fails loud if nothing is recognized — a guard against the seam with OE's authoritative #187
    MANIFEST, which uses a richer `[[entry]] + disposition` schema this interim loader does not yet
    read. Without this, the #187 manifest would parse to an empty Manifest and assemble would produce
    a silently-empty bundle (SA #188 seam contract, Risk 1). RECONCILIATION TRACKED: this loader must
    be adapted to the #187 disposition schema (as_is→copy · template→render · declared/exclude→tracked
    not copied · config_source/generated→explicit) before the two are wired together.
    """
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    templates = [(entry["src"], entry["dest"]) for entry in data.get("template", [])]
    as_is = [(entry["src"], entry["dest"]) for entry in data.get("as_is", [])]
    if not templates and not as_is:
        raise AssemblyError(
            f"manifest {path} has no recognized [[template]]/[[as_is]] entries — schema mismatch? "
            "(the #187 disposition schema is not yet read by this interim loader)"
        )
    return Manifest(templates=templates, as_is=as_is)


def _write(out_dir: Path, dest: str, content: str) -> None:
    """Writes content to out_dir/dest, creating parent directories."""
    target = out_dir / dest
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)


def assemble(manifest: Manifest, repo_root: Path, out_dir: Path) -> list[str]:
    """Produces the bundle under out_dir: render templates from seed.toml, copy as-is files verbatim.

    Reads the config from `<repo_root>/seed/seed.toml`. Fails loud (AssemblyError) on any missing
    source — an incomplete bundle is worse than none. Returns the list of produced destination paths.
    """
    config = render.load_seed_config(repo_root / "seed" / "seed.toml")
    produced: list[str] = []

    for src, dest in manifest.templates:
        source = repo_root / src
        if not source.is_file():
            raise AssemblyError(f"manifest template source not found: {src}")
        _write(out_dir, dest, render.render(source.read_text(), config))
        produced.append(dest)

    for src, dest in manifest.as_is:
        source = repo_root / src
        if not source.is_file():
            raise AssemblyError(f"manifest as-is source not found: {src}")
        target = out_dir / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        produced.append(dest)

    return produced
