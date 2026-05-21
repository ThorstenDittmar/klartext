"""Base exception classes for all klartext application errors."""


class KlartextError(Exception):
    """Root exception for all klartext errors."""


class DomainError(KlartextError):
    """Raised by domain objects when invariants are violated."""


class ServiceError(KlartextError):
    """Raised by services when business rules are violated."""


class RepositoryError(KlartextError):
    """Raised by repositories when data access fails."""
