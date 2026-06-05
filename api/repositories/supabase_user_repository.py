"""Adapter: persists and loads Users via Supabase (PostgREST)."""

from __future__ import annotations

import logging

from supabase import AsyncClient

from api.exceptions.user import UserNotFoundError, UserValidationError
from api.models.user import User
from api.repositories._supabase import records
from api.repositories.user_repository import UserRepository

_USER_TABLE = "users"

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


class SupabaseUserRepository(UserRepository):
    """Reads and writes Users using the Supabase PostgREST API."""

    logger = logging.getLogger(__name__)

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def find_by_id(self, user_id: str) -> User:
        """Returns the User with the given ID.

        Raises UserNotFoundError if no row exists for the given ID.
        """
        self.logger.debug("SupabaseUserRepository.find_by_id: user_id=%s", user_id)
        result = await self._client.table(_USER_TABLE).select("*").eq("id", user_id).execute()
        if not result.data:
            raise UserNotFoundError(f"User not found: {user_id}")
        return User.from_record(records(result.data)[0])

    async def find_default(self) -> User:
        """Returns the auto-logged-in default user (Thorsten).

        Raises UserNotFoundError if the default user has not been seeded.
        """
        self.logger.debug("SupabaseUserRepository.find_default")
        return await self.find_by_id(DEFAULT_USER_ID)

    async def add(self, user: User) -> User:
        """Inserts a new User row and returns it with its assigned ID.

        Raises UserValidationError if the user name is empty.
        """
        self.logger.info("SupabaseUserRepository.add: name=%s", user.name)
        if not user.name.strip():
            raise UserValidationError("name must not be empty")
        result = await self._client.table(_USER_TABLE).insert({"name": user.name}).execute()
        if not result.data:
            raise UserValidationError("Add returned no data for user.")
        return User.from_record(records(result.data)[0])

    async def update(self, user: User) -> User:
        """Persists changes to an existing User. Returns the updated User.

        Raises UserNotFoundError if no row exists for the given ID.
        """
        self.logger.info("SupabaseUserRepository.update: user_id=%s", user.id)
        result = (
            await self._client.table(_USER_TABLE)
            .update({"name": user.name})
            .eq("id", user.id)
            .execute()
        )
        if not result.data:
            raise UserNotFoundError(f"User not found: {user.id}")
        return User.from_record(records(result.data)[0])

    async def remove(self, user_id: str) -> None:
        """Deletes the User with the given ID.

        Raises UserNotFoundError if no row exists for the given ID.
        """
        self.logger.info("SupabaseUserRepository.remove: user_id=%s", user_id)
        result = await self._client.table(_USER_TABLE).delete().eq("id", user_id).execute()
        if not result.data:
            raise UserNotFoundError(f"User not found: {user_id}")
