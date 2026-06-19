"""Method-seed bundle assembly (Model B — OE bundling decision, user-ratified 2026-06-19).

seed/ stores only the seed-specific `.tmpl` files + this assembly mechanism + `MANIFEST.toml` (the
authoritative inventory, #187). `assemble` produces a self-contained bundle on demand, routing each
manifest entry by its disposition:

  * as_is / config_source → copy `path` verbatim from the live repo to `target`
  * template              → render `path` (a .tmpl) from seed.toml to `target`
  * declared / exclude    → never shipped (prerequisite the importer provides / product boundary)
  * deferred              → in-scope but not yet shippable → skipped, reported as a known gap
  * generated             → produced by assembly logic; none exist yet → fail loud if encountered

No as-is file is stored in seed/ — the single source of truth stays the live repo; the bundle is the
self-contained artefact. Stack-neutral (stdlib only; a Python runtime is a declared prerequisite).
"""

from __future__ import annotations

import shutil
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402 — sibling module; seed/ is on the path above (standalone-tool pattern)

# The #187 disposition taxonomy. Routing is grouped below; every entry must carry one of these.
_COPY_DISPOSITIONS = frozenset({"as_is", "config_source"})
_RENDER_DISPOSITIONS = frozenset({"template"})
_SKIP_DISPOSITIONS = frozenset({"declared", "exclude"})  # deliberately not shipped
_DEFERRED_DISPOSITION = "deferred"  # in-scope, not yet shippable → known gap
_GENERATED_DISPOSITION = (
    "generated"  # assembly-from-logic; none implemented yet → fail loud
)
KNOWN_DISPOSITIONS: frozenset[str] = (
    _COPY_DISPOSITIONS
    | _RENDER_DISPOSITIONS
    | _SKIP_DISPOSITIONS
    | {_DEFERRED_DISPOSITION, _GENERATED_DISPOSITION}
)


class AssemblyError(Exception):
    """Raised on a malformed manifest or a missing source — the bundle must never be silently partial."""


@dataclass(frozen=True)
class Entry:
    """One manifest entry: a source `path`, its `disposition`, the bundle `target`, and a note."""

    path: str
    disposition: str
    target: str
    note: str


@dataclass(frozen=True)
class Manifest:
    """The parsed seed manifest — the inventory the assembly step iterates."""

    entries: list[Entry]


@dataclass(frozen=True)
class AssembleResult:
    """Outcome of assembly: the targets produced, and the deferred entries (known gaps)."""

    produced: list[str]
    deferred: list[str]


def load_manifest(path: Path) -> Manifest:
    """Parses the #187 manifest (`[[entry]]` + disposition) into validated entries.

    Fails loud on a manifest with no entries (schema mismatch / empty) or any unknown disposition —
    the seam guard against silently diverging from the authoritative manifest (SA #188 contract).
    `target` defaults to `path` when absent (as-is files copy to their own location).
    """
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    raw_entries = data.get("entry", [])
    if not raw_entries:
        raise AssemblyError(
            f"manifest {path} has no [[entry]] tables — empty or wrong schema"
        )
    entries: list[Entry] = []
    for raw in raw_entries:
        disposition = raw.get("disposition", "")
        entry_path = raw.get("path", "")
        if disposition not in KNOWN_DISPOSITIONS:
            raise AssemblyError(
                f"manifest entry '{entry_path}' has an unknown disposition: {disposition!r}"
            )
        entries.append(
            Entry(
                path=entry_path,
                disposition=disposition,
                target=raw.get("target", entry_path),
                note=raw.get("note", ""),
            )
        )
    return Manifest(entries=entries)


def assemble(manifest: Manifest, repo_root: Path, out_dir: Path) -> AssembleResult:
    """Produces the bundle under out_dir per the manifest dispositions. Fails loud on any missing source.

    Reads the config from `<repo_root>/seed/seed.toml`. Returns the produced targets and the deferred
    entries (in-scope known gaps the completeness view surfaces).
    """
    config = render.load_seed_config(repo_root / "seed" / "seed.toml")
    produced: list[str] = []
    deferred: list[str] = []

    for entry in manifest.entries:
        if entry.disposition in _SKIP_DISPOSITIONS:
            continue
        if entry.disposition == _DEFERRED_DISPOSITION:
            deferred.append(entry.path)
            continue
        if entry.disposition == _GENERATED_DISPOSITION:
            raise AssemblyError(
                f"manifest entry '{entry.path}' is 'generated' — assembly-from-logic is not implemented"
            )
        source = repo_root / entry.path
        if not source.is_file():
            raise AssemblyError(
                f"manifest source not found: {entry.path} ({entry.disposition})"
            )
        target = out_dir / entry.target
        target.parent.mkdir(parents=True, exist_ok=True)
        if entry.disposition in _RENDER_DISPOSITIONS:
            target.write_text(render.render(source.read_text(), config))
        else:  # copy dispositions: as_is, config_source
            shutil.copyfile(source, target)
        produced.append(entry.target)

    return AssembleResult(produced=produced, deferred=deferred)
