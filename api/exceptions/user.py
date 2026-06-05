"""Exception classes for the User domain and related services."""

from api.exceptions.base import DomainError, RepositoryError


class UserError(DomainError):
    """Base class for all User-related domain errors."""


class UserValidationError(UserError):
    """Raised when a User cannot be constructed with the given values."""


class UserNotFoundError(RepositoryError):
    """Raised when a User cannot be found by the given identifier."""


class UserPersistenceError(RepositoryError):
    """Raised when a database operation on a User fails unexpectedly."""
