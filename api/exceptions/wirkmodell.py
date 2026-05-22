"""Exceptions for the Wirkmodell domain, service and repository layers."""

from __future__ import annotations

from api.exceptions.base import DomainError, RepositoryError, ServiceError


class WirkmodellValidationError(DomainError):
    """Raised by Wirkmodell or Axiom when invariants are violated."""


class AxiomValidationError(DomainError):
    """Raised by Axiom when invariants are violated."""


class WirkmodellNotFoundError(RepositoryError):
    """Raised by WirkmodellRepository when no Wirkmodell exists for the given ID."""


class WirkmodellPersistenceError(RepositoryError):
    """Raised by WirkmodellRepository when a database operation fails."""
