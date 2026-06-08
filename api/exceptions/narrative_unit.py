"""Exception classes for the NarrativeUnit domain, service and repository."""

from api.exceptions.base import DomainError, RepositoryError


class NarrativeUnitValidationError(DomainError):
    """Raised when a NarrativeUnit cannot be created due to invalid input."""


class InvalidOperationError(DomainError):
    """Raised when an operation is not valid for the target NarrativeUnit type.

    Example: calling update_title() on a Fragment, which has no title.
    """


class NarrativeUnitNotFoundError(RepositoryError):
    """Raised when a NarrativeUnit cannot be found by the given ID."""


class NarrativeUnitPersistenceError(RepositoryError):
    """Raised when saving, loading or deleting a NarrativeUnit fails."""
