

from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Candidate, DocumentRequest, DocumentSubmission


class ICandidateRepository(ABC):
    
    @abstractmethod
    def create(self, candidate: Candidate) -> Candidate:
        pass
    
    @abstractmethod
    def get_by_id(self, candidate_id: int) -> Optional[Candidate]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Candidate]:
        pass
    
    @abstractmethod
    def update(self, candidate: Candidate) -> Candidate:
        pass


class IDocumentRequestRepository(ABC):
    
    @abstractmethod
    def create(self, request: DocumentRequest) -> DocumentRequest:
        pass
    
    @abstractmethod
    def get_by_candidate_id(self, candidate_id: int) -> List[DocumentRequest]:
        pass
    
    @abstractmethod
    def update(self, request: DocumentRequest) -> DocumentRequest:
        pass


class IDocumentSubmissionRepository(ABC):
    
    @abstractmethod
    def create(self, submission: DocumentSubmission) -> DocumentSubmission:
        pass
    
    @abstractmethod
    def get_by_candidate_id(self, candidate_id: int) -> List[DocumentSubmission]:
        pass


class IEmailService(ABC):
    
    @abstractmethod
    def send_email(self, to_email: str, subject: str, message: str) -> bool:
        pass