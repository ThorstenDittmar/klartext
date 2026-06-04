"""Exception classes for the claim domain, extraction service and repository."""

from api.exceptions.base import DomainError, RepositoryError, ServiceError


class ClaimValidationError(DomainError):
    """Raised when a Claim cannot be created due to invalid input."""


class ClaimExtractionError(ServiceError):
    """Raised when claim extraction fails or yields no results."""


class ClaimPersistenceError(RepositoryError):
    """Raised when saving or loading Claims fails due to a database error."""


class ClaimNotFoundError(RepositoryError):
    """Raised by ClaimRepository when no Claim exists for the given ID."""
