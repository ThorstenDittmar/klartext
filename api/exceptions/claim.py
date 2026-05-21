"""Exception classes for the claim domain and extraction service."""

from api.exceptions.base import DomainError, ServiceError


class ClaimValidationError(DomainError):
    """Raised when a Claim cannot be created due to invalid input."""


class ClaimExtractionError(ServiceError):
    """Raised when claim extraction fails or yields no results."""
