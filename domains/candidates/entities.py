#Domain Entities

from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime




from .value_objects import (
    ExtractionStatus,
    DocumentType,
    RequestType,
    CommunicationChannel,
    VerificationStatus,
    RequestStatus,
    ExtractedData,
    DocumentRequestMessage,
)


@dataclass
class Candidate:
    
    """Domain entity representing a candidate."""
    
    id: Optional[int] = None
    name: str = ''
    email: str = ''
    phone: str = ''
    company: str = ''
    designation: str = ''
    skills: List[str] = field(default_factory=list)
    resume_file_path: str = ''
    extraction_status: ExtractionStatus = ExtractionStatus.PENDING
    extraction_confidence: float = 0.0
    raw_extracted_data: dict = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def update_extraction_data(self, extracted_data: ExtractedData) -> None:
        """Update candidate with extracted data."""
        self.name = extracted_data.name
        self.email = extracted_data.email
        self.phone = extracted_data.phone
        self.company = extracted_data.company
        self.designation = extracted_data.designation
        self.skills = extracted_data.skills
        self.extraction_confidence = extracted_data.confidence
        self.raw_extracted_data = extracted_data.raw_data
        self.extraction_status = ExtractionStatus.COMPLETED

    def mark_extraction_failed(self, error: str) -> None:
        """Mark extraction as failed."""
        self.extraction_status = ExtractionStatus.FAILED
        self.raw_extracted_data = {'error': error}

    def mark_extraction_processing(self) -> None:
        """Mark extraction as processing."""
        self.extraction_status = ExtractionStatus.PROCESSING

    def is_extraction_complete(self) -> bool:
        """Check if extraction is complete."""
        return self.extraction_status == ExtractionStatus.COMPLETED


@dataclass
class DocumentRequest:
    """Domain entity representing a document request."""
    id: Optional[int] = None
    candidate_id: int = 0
    request_type: RequestType = RequestType.BOTH
    request_message: str = ''
    communication_channel: CommunicationChannel = CommunicationChannel.EMAIL
    status: RequestStatus = RequestStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def update_message(self, message: DocumentRequestMessage) -> None:
        """Update request with generated message."""
        self.request_message = message.message
        self.request_type = message.request_type
        self.communication_channel = message.communication_channel

    def mark_as_sent(self) -> None:
        """Mark request as sent."""
        self.status = RequestStatus.SENT


@dataclass
class DocumentSubmission:
    """Domain entity representing a submitted document."""
    id: Optional[int] = None
    candidate_id: int = 0
    document_type: DocumentType = DocumentType.PAN
    document_file_path: str = ''
    verification_status: VerificationStatus = VerificationStatus.PENDING
    uploaded_at: Optional[datetime] = None

    def mark_as_verified(self) -> None:
        """Mark document as verified."""
        self.verification_status = VerificationStatus.VERIFIED

    def mark_as_rejected(self) -> None:
        """Mark document as rejected."""
        self.verification_status = VerificationStatus.REJECTED

