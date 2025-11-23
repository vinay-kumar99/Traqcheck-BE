#Domain service

from typing import Dict, Any
from .value_objects import ExtractedData


class ExtractionConfidenceCalculator:
    """Domain service to calculate extraction confidence."""
    
    @staticmethod
    def calculate(extracted_data: Dict[str, Any]) -> float:
        
        """Calculate confidence score based on extracted fields."""
        
        fields = ['name', 'email', 'phone', 'company', 'designation', 'skills']
        filled_fields = sum(1 for field in fields if extracted_data.get(field))
        return filled_fields / len(fields) if fields else 0.0


# Creating classes and its abstract method which is not implemented for now
# this will be used incase if there are multiple type


class ResumeTextExtractor:
    
    def extract(self, file_path: str) -> str:

        raise NotImplementedError("Subclasses must implement extract method")


class ResumeDataExtractor:
    
    def extract(self, resume_text: str) -> ExtractedData:

        raise NotImplementedError("Subclasses must implement extract method")


class DocumentRequestGenerator:
    
    def generate(
        self,
        candidate_name: str,
        candidate_email: str,
        candidate_phone: str,
        request_type: str,
        communication_channel: str,
    ) -> str:
        
        raise NotImplementedError("Subclasses must implement generate method")

