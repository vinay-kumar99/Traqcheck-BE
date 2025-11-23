from enum import Enum
from typing import List, Dict, Any
from dataclasses import dataclass


class ExtractionStatus(Enum):
    """Status of resume extraction process."""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'


class DocumentType(Enum):
    """Type of identity document."""
    PAN = 'pan'
    AADHAAR = 'aadhaar'


class RequestType(Enum):
    """Type of document request."""
    PAN = 'pan'
    AADHAAR = 'aadhaar'
    BOTH = 'both'


class CommunicationChannel(Enum):
    """Communication channel for document requests."""
    EMAIL = 'email'
    PHONE = 'phone'
    BOTH = 'both'


class VerificationStatus(Enum):
    """Status of document verification."""
    PENDING = 'pending'
    VERIFIED = 'verified'
    REJECTED = 'rejected'


class RequestStatus(Enum):
    """Status of document request."""
    PENDING = 'pending'
    SENT = 'sent'
    COMPLETED = 'completed'


@dataclass(frozen=True)
class ExtractedData:
    """Value object representing extracted candidate data."""
    name: str
    email: str
    phone: str
    company: str
    designation: str
    skills: List[str]
    confidence: float
    raw_data: Dict[str, Any]

    def __post_init__(self):
        """Validate extracted data."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        if not isinstance(self.skills, list):
            raise ValueError("Skills must be a list")


@dataclass(frozen=True)
class DocumentRequestMessage:
    """Value object representing a document request message."""
    message: str
    request_type: RequestType
    communication_channel: CommunicationChannel

    def __post_init__(self):
        """Validate message."""
        if not self.message or not self.message.strip():
            raise ValueError("Message cannot be empty")

