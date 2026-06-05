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

    async def add(self, user: User) -> User:
        """Adds a new User to the in-memory store and returns it."""
        self.logger.info("FakeUserRepository.add: user_id=%s", user.id)
        self._store[user.id] = user  # type: ignore[index]
        return user

    async def update(self, user: User) -> User:
        """Updates an existing User in the in-memory store. Raises UserNotFoundError if absent."""
        self.logger.info("FakeUserRepository.update: user_id=%s", user.id)
        if user.id not in self._store:
            raise UserNotFoundError(f"User not found: {user.id}")
        self._store[user.id] = user  # type: ignore[index]
        return user

    async def remove(self, user_id: str) -> None:
        """Removes a User from the in-memory store. Raises UserNotFoundError if absent."""
        self.logger.info("FakeUserRepository.remove: user_id=%s", user_id)
        if user_id not in self._store:
            raise UserNotFoundError(f"User not found: {user_id}")
        del self._store[user_id]
