
from typing import List, Optional
from datetime import datetime
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
    RequestStatus,
    VerificationStatus,
)
from domains.candidates.interfaces import (
    ICandidateRepository,
    IDocumentRequestRepository,
    IDocumentSubmissionRepository,
)
from .models import (
    CandidateModel,
    DocumentRequestModel,
    DocumentSubmissionModel,
)


class CandidateRepository(ICandidateRepository):
    
    def create(self, candidate: Candidate) -> Candidate:
        resume_file = candidate.resume_file_path
        if hasattr(candidate.resume_file_path, 'name'):
            resume_file = candidate.resume_file_path
        
        model = CandidateModel.objects.create(
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            company=candidate.company,
            designation=candidate.designation,
            skills=candidate.skills,
            resume_file=resume_file,
            extraction_status=candidate.extraction_status.value,
            extraction_confidence=candidate.extraction_confidence,
            raw_extracted_data=candidate.raw_extracted_data,
        )
        return self._to_entity(model)
    
    def get_by_id(self, candidate_id: int) -> Optional[Candidate]:
        try:
            model = CandidateModel.objects.get(pk=candidate_id)
            return self._to_entity(model)
        except CandidateModel.DoesNotExist:
            return None
    
    def get_all(self) -> List[Candidate]:
        models = CandidateModel.objects.all()
        return [self._to_entity(m) for m in models]
    
    def update(self, candidate: Candidate) -> Candidate:
        if not candidate.id:
            raise ValueError("Candidate must have an ID to update")
        
        model = CandidateModel.objects.get(pk=candidate.id)
        model.name = candidate.name
        model.email = candidate.email
        model.phone = candidate.phone
        model.company = candidate.company
        model.designation = candidate.designation
        model.skills = candidate.skills
        model.extraction_status = candidate.extraction_status.value
        model.extraction_confidence = candidate.extraction_confidence
        model.raw_extracted_data = candidate.raw_extracted_data
        model.save()
        
        return self._to_entity(model)
    
    def _to_entity(self, model: CandidateModel) -> Candidate:
        return Candidate(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            company=model.company,
            designation=model.designation,
            skills=model.skills,
            resume_file_path=model.resume_file.name if model.resume_file else '',
            extraction_status=ExtractionStatus(model.extraction_status),
            extraction_confidence=model.extraction_confidence or 0.0,
            raw_extracted_data=model.raw_extracted_data,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class DocumentRequestRepository(IDocumentRequestRepository):
    
    def create(self, request: DocumentRequest) -> DocumentRequest:
        
        candidate_model = CandidateModel.objects.get(pk=request.candidate_id)
        model = DocumentRequestModel.objects.create(
            candidate=candidate_model,
            request_type=request.request_type.value,
            request_message=request.request_message,
            communication_channel=request.communication_channel.value,
            status=request.status.value,
        )
        return self._to_entity(model)
    
    def get_by_candidate_id(self, candidate_id: int) -> List[DocumentRequest]:
        models = DocumentRequestModel.objects.filter(candidate_id=candidate_id)
        return [self._to_entity(m) for m in models]
    
    def update(self, request: DocumentRequest) -> DocumentRequest:
        if not request.id:
            raise ValueError("Request must have an ID to update")
        
        model = DocumentRequestModel.objects.get(pk=request.id)
        model.status = request.status.value
        model.save()
        return self._to_entity(model)
    
    def _to_entity(self, model: DocumentRequestModel) -> DocumentRequest:
        
        return DocumentRequest(
            id=model.id,
            candidate_id=model.candidate_id,
            request_type=RequestType(model.request_type),
            request_message=model.request_message,
            communication_channel=CommunicationChannel(model.communication_channel),
            status=RequestStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class DocumentSubmissionRepository(IDocumentSubmissionRepository):
    
    def create(self, submission: DocumentSubmission) -> DocumentSubmission:
        
        
        candidate_model = CandidateModel.objects.get(pk=submission.candidate_id)
        
        document_file = submission.document_file_path
        if hasattr(submission.document_file_path, 'name'):
            
            document_file = submission.document_file_path
        
        model = DocumentSubmissionModel.objects.create(
            candidate=candidate_model,
            document_type=submission.document_type.value,
            document_file=document_file,
            verification_status=submission.verification_status.value,
        )
        return self._to_entity(model)
    
    def get_by_candidate_id(self, candidate_id: int) -> List[DocumentSubmission]:
        
        models = DocumentSubmissionModel.objects.filter(candidate_id=candidate_id)
        return [self._to_entity(m) for m in models]
    
    def _to_entity(self, model: DocumentSubmissionModel) -> DocumentSubmission:
        
        return DocumentSubmission(
            id=model.id,
            candidate_id=model.candidate_id,
            document_type=DocumentType(model.document_type),
            document_file_path=model.document_file.name if model.document_file else '',
            verification_status=VerificationStatus(model.verification_status),
            uploaded_at=model.uploaded_at,
        )

