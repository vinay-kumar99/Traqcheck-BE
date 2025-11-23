from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


from applications.candidates.use_cases import (
    UploadResumeUseCase,
    GetCandidatesUseCase,
    GetCandidateDetailUseCase,
    RequestDocumentsUseCase,
    SubmitDocumentUseCase,
)
from applications.candidates.dto import (
    UploadResumeRequest,
    RequestDocumentsRequest,
    SubmitDocumentRequest,
)
from domains.candidates.exceptions import (
    CandidateNotFoundError,
    InvalidResumeFileError,
    ExtractionFailedError,
)
from infrastructure.persistence.repositories import (
    CandidateRepository,
    DocumentRequestRepository,
    DocumentSubmissionRepository,
)
from infrastructure.external.file_parsers import ResumeTextExtractorFactory
from infrastructure.external.ai_services import (
    OpenRouterResumeDataExtractor,
    OpenRouterDocumentRequestGenerator,
)
from infrastructure.external.email_services import EmailService


from .serializers import (
    CandidateListSerializer,
    CandidateUploadSerializer,
    DocumentRequestSerializer,
    DocumentSubmissionSerializer,
    RequestDocumentsSerializer,
    SubmitDocumentSerializer,
)


from domains.candidates.entities import DocumentRequest
from domains.candidates.value_objects import RequestStatus




class CandidateViewSet(viewsets.ViewSet):
    
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def _get_upload_use_case(self) -> UploadResumeUseCase:
        candidate_repo = CandidateRepository()
        text_extractor_factory = ResumeTextExtractorFactory()
        data_extractor = OpenRouterResumeDataExtractor()
        
        return UploadResumeUseCase(
            candidate_repository=candidate_repo,
            text_extractor=None,
            data_extractor=data_extractor,
        )
    
    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        
        serializer = CandidateUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            resume_file = serializer.validated_data['resume_file']
            
            # Create text extractor for this file
            text_extractor = ResumeTextExtractorFactory.create(resume_file.name)
            
            # Create use case with dependencies
            candidate_repo = CandidateRepository()
            data_extractor = OpenRouterResumeDataExtractor()
            use_case = UploadResumeUseCase(
                candidate_repository=candidate_repo,
                text_extractor=text_extractor,
                data_extractor=data_extractor,
            )
            
            # Execute use case
            upload_request = UploadResumeRequest(resume_file=resume_file)
            candidate_dto = use_case.execute(upload_request)
            
            # Convert DTO to response
            response_data = self._candidate_dto_to_dict(candidate_dto, request)
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except (InvalidResumeFileError, ExtractionFailedError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    def list(self, request):
        try:
            use_case = GetCandidatesUseCase(
                candidate_repository=CandidateRepository(),
            )
            candidates = use_case.execute()
            
            serializer = CandidateListSerializer(candidates, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    def retrieve(self, request, pk=None):
        
        try:
            use_case = GetCandidateDetailUseCase(
                candidate_repository=CandidateRepository(),
                request_repository=DocumentRequestRepository(),
                submission_repository=DocumentSubmissionRepository(),
            )
            detail_dto = use_case.execute(int(pk))
            
            response_data = self._detail_dto_to_dict(detail_dto, request)
            
            return Response(response_data)
        except CandidateNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=True, methods=['post'], url_path='request-documents')
    def request_documents(self, request, pk=None):
        """Generate and log AI document request."""
        
        
        print(request.data)
        
        
        serializer = RequestDocumentsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

        
        try:
            use_case = RequestDocumentsUseCase(
                candidate_repository=CandidateRepository(),
                request_repository=DocumentRequestRepository(),
                message_generator=OpenRouterDocumentRequestGenerator(),
                email_service=EmailService(),
            )
            
            request_dto = RequestDocumentsRequest(
                request_type=serializer.validated_data['request_type'],
                communication_channel=serializer.validated_data['communication_channel'],
            )
            
            doc_request_dto = use_case.execute(int(pk), request_dto)
            

            if doc_request_dto.id:
                repo = DocumentRequestRepository()
                # Get the entity and update it
                
                req_entity = DocumentRequest(
                    id=doc_request_dto.id,
                    candidate_id=int(pk),
                    request_type=doc_request_dto.request_type,
                    request_message=doc_request_dto.request_message,
                    communication_channel=doc_request_dto.communication_channel,
                    status=RequestStatus.SENT,
                )
                updated = repo.update(req_entity)
                doc_request_dto.status = updated.status.value
            
            serializer = DocumentRequestSerializer(doc_request_dto)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except CandidateNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=True, methods=['post'], url_path='submit-documents')
    def submit_documents(self, request, pk=None):
        """Handle document submission."""
        
        
        serializer = SubmitDocumentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if serializer.validated_data['document_type'] not in ['pan', 'aadhaar']:
                return Response(
                    {'error': 'document_type must be "pan" or "aadhaar"'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            use_case = SubmitDocumentUseCase(
                candidate_repository=CandidateRepository(),
                submission_repository=DocumentSubmissionRepository(),
            )
            
            submit_request = SubmitDocumentRequest(
                document_type=serializer.validated_data['document_type'],
                document_file=serializer.validated_data['document_file'],
            )
            
            submission_dto = use_case.execute(int(pk), submit_request)
            serializer = DocumentSubmissionSerializer(submission_dto)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except CandidateNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    def _candidate_dto_to_dict(self, dto, request):
        """Convert candidate DTO to dict for response."""
        
        
        # Get file URL from model if available
        resume_file_url = dto.resume_file_url
        if dto.id and not resume_file_url:
            from infrastructure.persistence.models import CandidateModel
            try:
                model = CandidateModel.objects.get(pk=dto.id)
                if model.resume_file:
                    resume_file_url = request.build_absolute_uri(model.resume_file.url)
            except CandidateModel.DoesNotExist:
                pass
            
            
        
        return {
            'id': dto.id,
            'name': dto.name,
            'email': dto.email,
            'phone': dto.phone,
            'company': dto.company,
            'designation': dto.designation,
            'skills': dto.skills,
            'resume_file': resume_file_url,
            'extraction_status': dto.extraction_status,
            'extraction_confidence': dto.extraction_confidence,
            'raw_extracted_data': dto.raw_extracted_data,
            'created_at': dto.created_at,
            'updated_at': dto.updated_at,
        }
    
    def _detail_dto_to_dict(self, dto, request):
        """Convert detail DTO to dict for response."""
        
        
        candidate_dict = self._candidate_dto_to_dict(dto.candidate, request)
        candidate_dict['document_requests'] = [
            {
                'id': r.id,
                'request_type': r.request_type,
                'request_message': r.request_message,
                'communication_channel': r.communication_channel,
                'status': r.status,
                'created_at': r.created_at,
            }
            for r in dto.document_requests
        ]
        # Get file URLs for submissions
        from infrastructure.persistence.models import DocumentSubmissionModel
        submissions_list = []
        for s in dto.document_submissions:
            doc_file_url = s.document_file_url
            if s.id and not doc_file_url:
                try:
                    sub_model = DocumentSubmissionModel.objects.get(pk=s.id)
                    if sub_model.document_file:
                        doc_file_url = request.build_absolute_uri(sub_model.document_file.url)
                except DocumentSubmissionModel.DoesNotExist:
                    pass
            
            submissions_list.append({
                'id': s.id,
                'document_type': s.document_type,
                'document_file': doc_file_url,
                'verification_status': s.verification_status,
                'uploaded_at': s.uploaded_at,
            })
        
        candidate_dict['document_submissions'] = submissions_list
        return candidate_dict

