"""Domain object: a registered author who owns Narratives."""

from __future__ import annotations

from typing import Any

from api.exceptions.user import UserValidationError


class User:
    """An author who owns Narratives.

    At this stage only a name is stored. Authentication and full profiles
    are out of scope — a single default user is seeded and auto-logged-in.

    Invariants enforced at construction time:
    - name must not be empty or whitespace-only
    """

    def __init__(self, id: str | None, name: str) -> None:
        self._id = id
        self._name = name

    @classmethod
    def create(cls, name: str) -> User:
        """Creates a new User. Raises UserValidationError for empty name."""
        if not name.strip():
            raise UserValidationError("name must not be empty")
        return cls(id=None, name=name)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> User:
        """Reconstructs a User from a database record."""
        return cls(id=record["id"], name=record["name"])

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def name(self) -> str:
        return self._name
