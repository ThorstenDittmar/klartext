"""Exceptions for the CausalModel domain, service and repository layers."""

from __future__ import annotations

from api.exceptions.base import DomainError, RepositoryError


class CausalModelValidationError(DomainError):
    """Raised by CausalModel or Axiom when invariants are violated."""


class AxiomValidationError(DomainError):
    """Raised by Axiom when invariants are violated."""


class CausalModelNotFoundError(RepositoryError):
    """Raised by CausalModelRepository when no CausalModel exists for the given ID."""


class CausalModelPersistenceError(RepositoryError):
    """Raised by CausalModelRepository when a database operation fails."""
