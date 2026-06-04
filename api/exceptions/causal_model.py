"""Exceptions for the CausalModel domain, service and repository layers."""

from __future__ import annotations

from api.exceptions.base import DomainError, RepositoryError


class CausalModelValidationError(DomainError):
    """Raised by CausalModel or Axiom when invariants are violated."""


class AxiomValidationError(DomainError):
    """Raised by Axiom when invariants are violated."""


class SlotValidationError(DomainError):
    """Raised by Slot when invariants are violated (empty identifier, unknown type)."""


class CausalRelationValidationError(DomainError):
    """Raised by CausalRelation or DefinitoryRelation when invariants are violated."""


class NamespaceConflictError(DomainError):
    """Raised by CausalModel or CausalMixin when an identifier is already in use."""


class ScopeConflictError(DomainError):
    """Raised by CausalModel.add() when a component scope is incompatible with the model scope."""


class ConditionConflictError(DomainError):
    """Raised when two conditions on the same Slot require incompatible states."""


class CausalModelNotFoundError(RepositoryError):
    """Raised by CausalModelRepository when no CausalModel exists for the given ID."""


class CausalModelPersistenceError(RepositoryError):
    """Raised by CausalModelRepository when a database operation fails."""


class SlotNotFoundError(RepositoryError):
    """Raised by CausalModelRepository when no Slot exists for the given ID."""


class CausalRelationNotFoundError(RepositoryError):
    """Raised by CausalModelRepository when no CausalRelation exists for the given ID."""
