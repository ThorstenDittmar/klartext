"""Exception classes for the narrative domain, import service and repository."""

from api.exceptions.base import DomainError, RepositoryError, ServiceError


class SceneValidationError(DomainError):
    """Raised when a Scene cannot be created due to invalid input."""


class NarrativeValidationError(DomainError):
    """Raised when a Narrative cannot be created due to invalid input."""


class ActorValidationError(DomainError):
    """Raised when an Actor cannot be created due to invalid input."""


class NarrativeFileNotFoundError(ServiceError):
    """Raised when the narrative file does not exist at the given path."""


class NarrativeParseError(ServiceError):
    """Raised when the narrative file exists but contains no parseable scenes."""


class SceneNotFoundError(ServiceError):
    """Raised when a Scene with the given ID is not part of the requested Narrative."""


class ActorNotFoundError(ServiceError):
    """Raised when an Actor with the given ID is not part of the requested Narrative."""


class NarrativeNotFoundError(RepositoryError):
    """Raised when a Narrative cannot be found by the given ID."""


class NarrativePersistenceError(RepositoryError):
    """Raised when saving or loading a Narrative fails due to a database error."""


class NarrativeAnalysisError(ServiceError):
    """Raised when narrative analysis fails (e.g. provider error or invalid response)."""


class WirkgefuegeSuggestionError(ServiceError):
    """Raised when Wirkgefüge suggestion fails (e.g. provider error or invalid response)."""
