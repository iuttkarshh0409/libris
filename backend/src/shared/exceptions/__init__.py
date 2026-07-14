class DomainException(Exception):
    """Base exception class for all domain-specific errors."""

    pass


class ValidationException(DomainException):
    """Raised when domain rule or contract validation fails."""

    pass


class ConfigurationException(DomainException):
    """Raised when application configuration is missing or invalid."""

    pass


class RetrievalException(DomainException):
    """Raised when query context retrieval fails."""

    pass


class ProviderException(DomainException):
    """Raised when external provider operations fail (e.g. LLM, vector database)."""

    pass


__all__ = [
    "ConfigurationException",
    "DomainException",
    "ProviderException",
    "RetrievalException",
    "ValidationException",
]
