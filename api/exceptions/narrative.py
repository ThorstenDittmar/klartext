"""Exception classes for the narrative domain and import service."""

from api.exceptions.base import DomainError, ServiceError


class SceneValidationError(DomainError):
    """Raised when a Scene cannot be created due to invalid input."""


class NarrativeValidationError(DomainError):
    """Raised when a Narrative cannot be created due to invalid input."""


class NarrativeFileNotFoundError(ServiceError):
    """Raised when the narrative file does not exist at the given path."""


class NarrativeParseError(ServiceError):
    """Raised when the narrative file exists but contains no parseable scenes."""
