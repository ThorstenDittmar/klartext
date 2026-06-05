"""Port: defines the contract for loading Users."""

from __future__ import annotations

from abc import ABC, abstractmethod

from api.models.user import User


class UserRepository(ABC):
    """Abstract base class for all UserRepository implementations.

    Concrete adapters (e.g. SupabaseUserRepository) implement the actual
    data access. Tests inject a FakeUserRepository.
    """

    @abstractmethod
    async def find_by_id(self, user_id: str) -> User:
        """Returns the User with the given ID.

        Raises UserNotFoundError if no User exists for that ID.
        """

    @abstractmethod
    async def find_default(self) -> User:
        """Returns the auto-logged-in default user (Thorsten).

        Raises UserNotFoundError if the default user has not been seeded.
        """
