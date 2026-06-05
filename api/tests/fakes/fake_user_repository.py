"""FakeUserRepository — in-memory UserRepository for unit tests."""

from __future__ import annotations

import logging

from api.exceptions.user import UserNotFoundError
from api.models.user import User
from api.repositories.user_repository import UserRepository

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


class FakeUserRepository(UserRepository):
    """In-memory UserRepository for unit tests.

    Pre-seeded with the default user Thorsten so tests do not need
    to set up the database.
    """

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._store: dict[str, User] = {DEFAULT_USER_ID: User(id=DEFAULT_USER_ID, name="Thorsten")}

    async def find_by_id(self, user_id: str) -> User:
        """Returns the User with the given ID. Raises UserNotFoundError if absent."""
        self.logger.debug("FakeUserRepository.find_by_id: user_id=%s", user_id)
        if user_id not in self._store:
            raise UserNotFoundError(f"User not found: {user_id}")
        return self._store[user_id]

    async def find_default(self) -> User:
        """Returns the pre-seeded default user Thorsten."""
        self.logger.debug("FakeUserRepository.find_default")
        return await self.find_by_id(DEFAULT_USER_ID)
