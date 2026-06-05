"""UserService — business logic for User operations."""

from __future__ import annotations

import logging

from api.models.user import User
from api.repositories.user_repository import UserRepository


class UserService:
    """Provides business logic for User operations.

    Delegates all data access to the injected UserRepository.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def get_default(self) -> User:
        """Returns the auto-logged-in default user.

        Raises UserNotFoundError if the default user has not been seeded.
        """
        self.logger.debug("UserService.get_default")
        return await self._repository.find_default()

    async def get_by_id(self, user_id: str) -> User:
        """Returns the User with the given ID.

        Raises UserNotFoundError if no user exists for that ID.
        """
        self.logger.debug("UserService.get_by_id: user_id=%s", user_id)
        return await self._repository.find_by_id(user_id)
