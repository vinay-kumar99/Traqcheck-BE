"""
Domain exceptions for the candidates domain.
"""


class DomainException(Exception):
    """Base exception for domain errors."""
    pass


class CandidateNotFoundError(DomainException):
    """Raised when a candidate is not found."""
    pass


class InvalidResumeFileError(DomainException):
    """Raised when resume file is invalid."""
    pass


class ExtractionFailedError(DomainException):
    """Raised when resume extraction fails."""
    pass


class InvalidDocumentTypeError(DomainException):
    """Raised when document type is invalid."""
    pass


class DocumentRequestGenerationError(DomainException):
    """Raised when document request generation fails."""
    pass

