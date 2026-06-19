"""Standalone, stack-neutral Way-of-Working CLI logic (method-seed phase 4).

The seed ships this package as the importer's WoW CLI (git + stdlib only, no product stack).
klartext re-uses the same logic from api/cli.py, wiring its own paths — one entrypoint, no
regression. Extraction is incremental: skills first, then converge/landed/merge.
"""
