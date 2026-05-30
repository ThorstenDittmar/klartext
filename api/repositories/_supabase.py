"""Internal helpers for working with Supabase response data in a type-safe way.

Supabase's PostgREST client types `response.data` as `list[JSON]` where
`JSON = Union[None, bool, str, int, float, Sequence[JSON], Mapping[str, JSON]]`.
Mypy cannot narrow this union when accessing dictionary keys. The helpers in
this module cast the data to `list[dict[str, Any]]` at the repository boundary
so all downstream code is fully typed.
"""

from __future__ import annotations

from typing import Any, cast


def records(data: object) -> list[dict[str, Any]]:
    """Casts Supabase response data to a typed list of row records."""
    return cast(list[dict[str, Any]], data)
