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

# The scalar keys every seed.toml must carry. `cli_entrypoint` (phase 3) is the consumer's product
# CLI path the classify gate watches — parametrized, NOT a trigger-list literal (SA §9): api/ is the
# product stack, so the literal must not be baked into the generic WoW path list.
REQUIRED_KEYS: tuple[str, ...] = (
    "project_name",
    "env_prefix",
    "memory_dir",
    "product_domain",
    "repo_slug",
    "worktree_base",
    "identity_preamble",
    "interpreter",
    "cli_entrypoint",
)

# The list-valued keys every seed.toml must carry. `wow_trigger_paths` holds SA's generic-WoW
# classification (the paths whose change is a rolling-vs-breaking question, incl. .github/workflows/**);
# the rendered classify gate consumes it (plan §9).
REQUIRED_LISTS: tuple[str, ...] = ("wow_trigger_paths",)

# A template placeholder: {{key}}, with optional inner whitespace ({{ key }}).
_PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


class SeedConfigError(Exception):
    """Raised when seed.toml lacks a required key or a template references an unknown one."""


@dataclass(frozen=True)
class SeedConfig:
    """The validated seed config: scalar and list keys, accessed by name with type-checked getters."""

    values: dict[str, str | list[str]]

    def __getitem__(self, key: str) -> str:
        """Returns a scalar value. Fails loud if the key is missing or holds a list."""
        try:
            value = self.values[key]
        except KeyError:
            raise SeedConfigError(f"unknown seed config key: {key}") from None
        if isinstance(value, list):
            raise SeedConfigError(f"seed config key '{key}' holds a list, not a scalar")
        return value

    def get_list(self, key: str) -> list[str]:
        """Returns a list value. Fails loud if the key is missing or holds a scalar."""
        try:
            value = self.values[key]
        except KeyError:
            raise SeedConfigError(f"unknown seed config list key: {key}") from None
        if not isinstance(value, list):
            raise SeedConfigError(f"seed config key '{key}' is not a list")
        return value


def load_seed_config(path: Path) -> SeedConfig:
    """Loads and validates a seed.toml. Raises SeedConfigError naming any missing required key/list.

    A malformed file is wrapped as a SeedConfigError naming the path — this tool is importer-facing,
    so a bare TOMLDecodeError without "which seed.toml" context would be poor DX. Scalars are coerced
    to str; list values are preserved (each item coerced to str), so path lists survive intact.
    """
    with path.open("rb") as handle:
        try:
            data = tomllib.load(handle)
        except tomllib.TOMLDecodeError as exc:
            raise SeedConfigError(f"{path} is not valid TOML: {exc}") from exc
    missing = [key for key in (*REQUIRED_KEYS, *REQUIRED_LISTS) if key not in data]
    if missing:
        raise SeedConfigError(
            f"seed.toml is missing required key(s): {', '.join(missing)}"
        )
    values: dict[str, str | list[str]] = {}
    for key, value in data.items():
        if isinstance(value, list):
            values[key] = [str(item) for item in value]
        elif isinstance(value, dict):
            # seed.toml is a flat config; a nested [table] is an unexpected shape that would
            # otherwise str()-flatten to a dict repr and render garbage downstream. Fail loud.
            raise SeedConfigError(
                f"seed config key '{key}' is a table/section; only scalars and lists are supported"
            )
        else:
            values[key] = str(value)
    return SeedConfig(values)


def trigger_patterns_from_config(config: SeedConfig) -> list[str]:
    """Builds the classify-gate TRIGGER_PATTERNS from seed.toml: generic WoW paths + the product CLI.

    The config-driven gate (B-Seed-only) sources its patterns here instead of hardcoding them:
    `wow_trigger_paths` (SA's generic-WoW classification) plus the parametrized `cli_entrypoint`
    (the consumer's product CLI path, kept out of the generic list per SA §9).
    """
    return [*config.get_list("wow_trigger_paths"), config["cli_entrypoint"]]


def render(template: str, config: SeedConfig) -> str:
    """Substitutes every `{{key}}` placeholder from the config.

    Fails loud on an unknown placeholder (via SeedConfig.__getitem__) — a placeholder shipped
    unsubstituted to an importer is a silent bug, so the renderer refuses it.
    """
    return _PLACEHOLDER.sub(lambda match: config[match.group(1)], template)
