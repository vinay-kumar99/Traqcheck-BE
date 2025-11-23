"""
Data Transfer Objects (DTOs) for the candidates application layer.
DTOs are used to transfer data between layers.
"""



from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class CandidateDTO:
    # DTO for candidate data.
    id: Optional[int]
    name: str
    email: str
    phone: str
    company: str
    designation: str
    skills: List[str]
    resume_file_url: Optional[str]
    extraction_status: str
    extraction_confidence: Optional[float]
    raw_extracted_data: Dict[str, Any]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


@dataclass
class CandidateListDTO:
    #DTO for candidate list item.
    id: int
    name: str
    email: str
    phone: str
    company: str
    designation: str
    extraction_status: str
    created_at: datetime


@dataclass
class DocumentRequestDTO:
    #DTO for document request.
    id: Optional[int]
    request_type: str
    request_message: str
    communication_channel: str
    status: str
    created_at: Optional[datetime]


@dataclass
class DocumentSubmissionDTO:
    """DTO for document submission."""
    id: Optional[int]
    document_type: str
    document_file_url: Optional[str]
    verification_status: str
    uploaded_at: Optional[datetime]


@dataclass
class CandidateDetailDTO:
    """DTO for detailed candidate view."""
    candidate: CandidateDTO
    document_requests: List[DocumentRequestDTO]
    document_submissions: List[DocumentSubmissionDTO]


@dataclass
class UploadResumeRequest:
    """Request DTO for resume upload."""
    resume_file: Any # could add file type (or string for filename)


@dataclass
class RequestDocumentsRequest:
    """Request DTO for document request."""
    request_type: str
    communication_channel: str


@dataclass
class SubmitDocumentRequest:
    """Request DTO for document submission."""
    document_type: str
    document_file: Any # could add file type (or string for filename)

