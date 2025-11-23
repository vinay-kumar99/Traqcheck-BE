
"""
Use cases for the candidates application.
Use cases orchestrate domain objects and coordinate with repositories.
"""

from typing import List

# importing domains

from domains.candidates.entities import (
    Candidate,
    DocumentRequest,
    DocumentSubmission,
)
from domains.candidates.value_objects import (
    ExtractionStatus,
    RequestType,
    CommunicationChannel,
    DocumentType,
)
from domains.candidates.interfaces import (
    ICandidateRepository,
    IDocumentRequestRepository,
    IDocumentSubmissionRepository,
    IEmailService,
)
from domains.candidates.domain_services import (
    ResumeTextExtractor,
    ResumeDataExtractor,
    DocumentRequestGenerator,
)
from domains.candidates.exceptions import (
    CandidateNotFoundError,
    ExtractionFailedError,
)


# importing dtos

from .dto import (
    CandidateDTO,
    CandidateListDTO,
    CandidateDetailDTO,
    DocumentRequestDTO,
    DocumentSubmissionDTO,
    UploadResumeRequest,
    RequestDocumentsRequest,
    SubmitDocumentRequest,
)


# importing models
from infrastructure.persistence.models import CandidateModel


class UploadResumeUseCase:
    #Use case for uploading and parsing a resume
    
    def __init__(
        self, 
        candidate_repository: ICandidateRepository, 
        text_extractor: ResumeTextExtractor, 
        data_extractor: ResumeDataExtractor
    ):
    
        self.candidate_repository = candidate_repository
        self.text_extractor = text_extractor
        self.data_extractor = data_extractor
    
    def execute(self, request: UploadResumeRequest) -> CandidateDTO:
        #Execute resume upload and parsing
        
        
        # Create candidate entity with file
        candidate = Candidate(
            resume_file_path=request.resume_file,
            extraction_status=ExtractionStatus.PROCESSING,
        )
        
        
        
        # Save candidate first (this will save the file)
        candidate = self.candidate_repository.create(candidate)
        
        try:
            # Get the saved file path from the model
            # We need to get the model to access the file path
        
            model = CandidateModel.objects.get(pk=candidate.id)
            file_path = model.resume_file.path
            
            # Extract text from resume
            resume_text = self.text_extractor.extract(file_path)
            
            # Extract structured data
            extracted_data = self.data_extractor.extract(resume_text)
            
            # Update candidate with extracted data
            candidate.update_extraction_data(extracted_data)
            
        except Exception as e:
            candidate.mark_extraction_failed(str(e))
            # Update with error
            candidate = self.candidate_repository.update(candidate)
            raise ExtractionFailedError(f"Failed to extract resume data: {str(e)}")
        
        # Update candidate in repository
        candidate = self.candidate_repository.update(candidate)
        
        return self._to_dto(candidate)
    
    def _to_dto(self, candidate: Candidate) -> CandidateDTO:
        
        
        """Convert entity to DTO."""
        
        
        
        return CandidateDTO(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            company=candidate.company,
            designation=candidate.designation,
            skills=candidate.skills,
            resume_file_url=None,  # Will be set by infrastructure later ()
            extraction_status=candidate.extraction_status.value,
            extraction_confidence=candidate.extraction_confidence,
            raw_extracted_data=candidate.raw_extracted_data,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
        )


class GetCandidatesUseCase:
    #Use case for getting all candidates.
    
    
    def __init__(self, candidate_repository: ICandidateRepository):
        self.candidate_repository = candidate_repository
    
    
    def execute(self) -> List[CandidateListDTO]:
        """Execute get all candidates."""
        
        
        candidates = self.candidate_repository.get_all()
        return [self._to_dto(candidate) for candidate in candidates]
    
    def _to_dto(self, candidate: Candidate) -> CandidateListDTO:
        #Convert entity to list DTO.
        
        
        return CandidateListDTO(
            id=candidate.id or 0, # 0 incase its invalid (this case should not appear)
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            company=candidate.company,
            designation=candidate.designation,
            extraction_status=candidate.extraction_status.value,
            created_at=candidate.created_at or candidate.updated_at or None
        )


class GetCandidateDetailUseCase:
    #Use case for getting candidate details
    
    def __init__(self, candidate_repository: ICandidateRepository, request_repository: IDocumentRequestRepository, submission_repository: IDocumentSubmissionRepository):
        
        
        self.candidate_repository = candidate_repository
        self.request_repository = request_repository
        self.submission_repository = submission_repository
        
    
    def execute(self, candidate_id: int) -> CandidateDetailDTO:
        #Execute get candidate detail.
        
        
        candidate = self.candidate_repository.get_by_id(candidate_id)
        
        
        if not candidate:
            raise CandidateNotFoundError(f"Candidate with id {candidate_id} not found")
        
        requests = self.request_repository.get_by_candidate_id(candidate_id)
        submissions = self.submission_repository.get_by_candidate_id(candidate_id)
        
        return CandidateDetailDTO(
            candidate=self._candidate_to_dto(candidate),
            document_requests=[self._request_to_dto(r) for r in requests],
            document_submissions=[self._submission_to_dto(s) for s in submissions]
        )
    
    def _candidate_to_dto(self, candidate: Candidate) -> CandidateDTO:
        #Convert candidate entity to DTO.
        
        
        return CandidateDTO(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            company=candidate.company,
            designation=candidate.designation,
            skills=candidate.skills,
            resume_file_url=None,
            extraction_status=candidate.extraction_status.value,
            extraction_confidence=candidate.extraction_confidence,
            raw_extracted_data=candidate.raw_extracted_data,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at
        )
    
    def _request_to_dto(self, request: DocumentRequest) -> DocumentRequestDTO:
        #Convert request entity to DTO
        
        
        return DocumentRequestDTO(
            id=request.id,
            request_type=request.request_type.value,
            request_message=request.request_message,
            communication_channel=request.communication_channel.value,
            
            status=request.status.value,
            created_at=request.created_at
        )
    
    def _submission_to_dto(self, submission: DocumentSubmission) -> DocumentSubmissionDTO:
        #Convert submission entity to DTO.
        
        
        return DocumentSubmissionDTO(
            id=submission.id,
            document_type=submission.document_type.value,
            
            document_file_url=None,
            verification_status=submission.verification_status.value,
            uploaded_at=submission.uploaded_at
            
        )


class RequestDocumentsUseCase:
    #Use case for requesting documents.
    
    def __init__(
        self,
        candidate_repository: ICandidateRepository,
        request_repository: IDocumentRequestRepository,
        message_generator: DocumentRequestGenerator,
        email_service: IEmailService,
    ):
        self.candidate_repository = candidate_repository
        self.request_repository = request_repository
        self.message_generator = message_generator
        self.email_service = email_service
    
    def execute(self, candidate_id: int, request: RequestDocumentsRequest) -> DocumentRequestDTO:
        #Execute document request.
        
        candidate = self.candidate_repository.get_by_id(candidate_id)
        if not candidate:
            raise CandidateNotFoundError(f"Candidate with id {candidate_id} not found")
        
        # Generate message
        message_text = self.message_generator.generate(
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            candidate_phone=candidate.phone,
            request_type=request.request_type,
            communication_channel=request.communication_channel
        )
        
        # Create request entity
        doc_request = DocumentRequest(
            candidate_id=candidate_id,
            request_type=RequestType(request.request_type),
            request_message=message_text,
            communication_channel=CommunicationChannel(request.communication_channel)
        )
        
        
        # set up email service
        # if request.communication_channel in ['email', 'both']:
        #     subject = f"Document Request: {request.request_type.replace('_', ' ').title()}"
        #     self.email_service.send_email(
        #         to_email=candidate.email,
        #         subject=subject,
        #         message=message_text,
        #     )
        
        doc_request = self.request_repository.create(doc_request)
        doc_request.mark_as_sent()
        doc_request = self.request_repository.update(doc_request) if hasattr(self.request_repository, 'update') else doc_request
        
        return DocumentRequestDTO(
            id=doc_request.id,
            request_type=doc_request.request_type.value,
            request_message=doc_request.request_message,
            communication_channel=doc_request.communication_channel.value,
            status=doc_request.status.value,
            created_at=doc_request.created_at
        )


class SubmitDocumentUseCase:
    #Use case for submitting documents.
    
    def __init__(
        self,
        candidate_repository: ICandidateRepository,
        submission_repository: IDocumentSubmissionRepository,
    ):
        self.candidate_repository = candidate_repository
        self.submission_repository = submission_repository
    
    def execute(self, candidate_id: int, request: SubmitDocumentRequest) -> DocumentSubmissionDTO:
        #Execute document submission.
        
        
        candidate = self.candidate_repository.get_by_id(candidate_id)
        if not candidate:
            raise CandidateNotFoundError(f"Candidate with id {candidate_id} not found")
        


        submission = DocumentSubmission(
            candidate_id=candidate_id,
            document_type=DocumentType(request.document_type),
            document_file_path=request.document_file
        )
        
        submission = self.submission_repository.create(submission)
        
        return DocumentSubmissionDTO(
            id=submission.id,
            document_type=submission.document_type.value,
            document_file_url=None,
            
            verification_status=submission.verification_status.value,
            uploaded_at=submission.uploaded_at
        )

