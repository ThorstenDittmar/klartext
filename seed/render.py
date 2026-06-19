"""Method-seed config source loader + template renderer (export plan §4/§7, phase 1).

`seed.toml` is the single source of every endeavour-specific literal (project name, env prefix,
memory dir, repo slug, …). Every downstream artefact — settings.json, .pre-commit-config.yaml, the
WoW workflows, the CLI defaults, classify_gate's path lists, inbox.sh — is rendered from it, so an
importer adapts one file instead of running a fragile global find-replace.

This is the keystone every later phase consumes. It is deliberately stack-neutral (stdlib only:
tomllib + re); a Python runtime is a declared seed prerequisite anyway (plan §8).
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

# The §4 keys every seed.toml must carry. Path lists (TRIGGER_PATTERNS etc.) are deferred to
# phase 3 — they are SA-semantics, not part of this keystone (plan §9).
REQUIRED_KEYS: tuple[str, ...] = (
    "project_name",
    "env_prefix",
    "memory_dir",
    "product_domain",
    "repo_slug",
    "worktree_base",
    "identity_preamble",
    "interpreter",
)

# A template placeholder: {{key}}, with optional inner whitespace ({{ key }}).
_PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


class SeedConfigError(Exception):
    """Raised when seed.toml lacks a required key or a template references an unknown one."""


@dataclass(frozen=True)
class SeedConfig:
    """The validated seed config: every required key present, accessed by name."""

    values: dict[str, str]

    def __getitem__(self, key: str) -> str:
        try:
            return self.values[key]
        except KeyError:
            raise SeedConfigError(f"unknown seed config key: {key}") from None


def load_seed_config(path: Path) -> SeedConfig:
    """Loads and validates a seed.toml. Raises SeedConfigError naming any missing required key.

    A malformed file is wrapped as a SeedConfigError naming the path — this tool is importer-facing,
    so a bare TOMLDecodeError without "which seed.toml" context would be poor DX.
    """
    with path.open("rb") as handle:
        try:
            data = tomllib.load(handle)
        except tomllib.TOMLDecodeError as exc:
            raise SeedConfigError(f"{path} is not valid TOML: {exc}") from exc
    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise SeedConfigError(
            f"seed.toml is missing required key(s): {', '.join(missing)}"
        )
    return SeedConfig({key: str(value) for key, value in data.items()})


def render(template: str, config: SeedConfig) -> str:
    """Substitutes every `{{key}}` placeholder from the config.

    Fails loud on an unknown placeholder (via SeedConfig.__getitem__) — a placeholder shipped
    unsubstituted to an importer is a silent bug, so the renderer refuses it.
    """
    return _PLACEHOLDER.sub(lambda match: config[match.group(1)], template)
