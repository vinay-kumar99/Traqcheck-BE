"""
File parsing implementations for resume text extraction.
"""
import re
from pathlib import Path
from typing import Dict, Any
import PyPDF2
from docx import Document
from domains.candidates.domain_services import ResumeTextExtractor
from domains.candidates.exceptions import InvalidResumeFileError


class PDFTextExtractor(ResumeTextExtractor):
    """Extract text from PDF files."""
    
    def extract(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text() + '\n'
                return text
        except Exception as e:
            raise InvalidResumeFileError(f"Error reading PDF: {str(e)}")


class DOCXTextExtractor(ResumeTextExtractor):
    """Extract text from DOCX files."""
    
    def extract(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise InvalidResumeFileError(f"Error reading DOCX: {str(e)}")


class ResumeTextExtractorFactory:
    """Factory to create appropriate text extractor based on file type."""
    
    @staticmethod
    def create(file_path: str) -> ResumeTextExtractor:
        """Create text extractor based on file extension."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return PDFTextExtractor()
        elif file_ext == '.docx':
            return DOCXTextExtractor()
        else:
            raise InvalidResumeFileError(f"Unsupported file format: {file_ext}")

