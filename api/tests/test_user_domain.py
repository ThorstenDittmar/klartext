"""Unit tests for the User domain object."""

from __future__ import annotations

import pytest

from api.exceptions.user import UserValidationError
from api.models.user import User


def test_user_create_sets_name() -> None:
    """Expects a User with the given name to be returned."""
    user = User.create(name="Thorsten")
    assert user.name == "Thorsten"


def test_user_create_id_is_none_before_save() -> None:
    """Expects a new User to have no ID before being persisted."""
    user = User.create(name="Thorsten")
    assert user.id is None


def test_user_create_rejects_empty_name() -> None:
    """Expects UserValidationError for an empty name."""
    with pytest.raises(UserValidationError):
        User.create(name="")


def test_user_create_rejects_whitespace_name() -> None:
    """Expects UserValidationError for a whitespace-only name."""
    with pytest.raises(UserValidationError):
        User.create(name="   ")


def test_user_from_record_reconstructs() -> None:
    """Expects User.from_record to reconstruct a User from a database row."""
    user = User.from_record({"id": "abc-123", "name": "Thorsten"})
    assert user.id == "abc-123"
    assert user.name == "Thorsten"
