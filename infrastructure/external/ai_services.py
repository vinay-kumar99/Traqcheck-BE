import os
import re
import json
from openai import OpenAI
from decouple import config


from domains.candidates.domain_services import (
    ResumeDataExtractor,
    DocumentRequestGenerator,
)
from domains.candidates.value_objects import ExtractedData
from domains.candidates.domain_services import ExtractionConfidenceCalculator


class OpenRouterResumeDataExtractor(ResumeDataExtractor):
    """Extract structured data from resume text using OpenRouter."""
    
    def __init__(self):
        api_key = config('OPENROUTER_API_KEY', '')
        base_url = config('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = None
        self.confidence_calculator = ExtractionConfidenceCalculator()
    
    def extract(self, resume_text: str) -> ExtractedData:
        """Extract structured data from resume text."""
        if not self.client:
            return self._basic_extraction(resume_text)
        
        try:
            model = config('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo')
            
            prompt = f"""Extract the following information from this resume text and return it as a JSON object:
- name: Full name of the candidate
- email: Email address
- phone: Phone number
- company: Current or most recent company
- designation: Current or most recent job title
- skills: List of technical skills and competencies

Resume text:
{resume_text[:3000]}

Return ONLY a valid JSON object with these exact keys: name, email, phone, company, designation, skills.
For skills, return an array of strings.
If any information is not found, use an empty string for strings or empty array for skills.
"""
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a resume parser. Extract structured information and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
            )
            
            content = response.choices[0].message.content.strip()
            
            
            
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = re.sub(r'^```(?:json)?\n', '', content)
                content = re.sub(r'\n```$', '', content)
            
            extracted_dict = json.loads(content)
            
            # Calculate confidence
            confidence = self.confidence_calculator.calculate(extracted_dict)
            
            return ExtractedData(
                name=extracted_dict.get('name', ''),
                email=extracted_dict.get('email', ''),
                phone=extracted_dict.get('phone', ''),
                company=extracted_dict.get('company', ''),
                designation=extracted_dict.get('designation', ''),
                skills=extracted_dict.get('skills', []),
                confidence=confidence,
                raw_data=extracted_dict,
            )
            
            
        except Exception as e:
            # Fallback to basic extraction on error
            return self._basic_extraction(resume_text)
        
    
    def _basic_extraction(self, text: str) -> ExtractedData:
        """Basic regex-based extraction as fallback."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        # Try to extract name from first line
        lines = text.split('\n')
        name = lines[0].strip() if lines else ''
        
        extracted_dict = {
            'name': name[:255] if name else '',
            'email': emails[0] if emails else '',
            'phone': phones[0] if phones else '',
            'company': '',
            'designation': '',
            'skills': [],
        }
        
        confidence = self.confidence_calculator.calculate(extracted_dict)
        
        return ExtractedData(
            
            name=extracted_dict['name'],
            email=extracted_dict['email'],
            
            phone=extracted_dict['phone'],
            company=extracted_dict['company'],
            
            designation=extracted_dict['designation'],
            skills=extracted_dict['skills'],
            
            confidence=confidence,
            raw_data=extracted_dict,
        )


class OpenRouterDocumentRequestGenerator(DocumentRequestGenerator):
    """Generate document requests using OpenRouter."""
    
    def __init__(self):
        api_key = config('OPENROUTER_API_KEY', '')
        base_url = config('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = None
    
    def generate(
        self,
        candidate_name: str,
        candidate_email: str,
        candidate_phone: str,
        request_type: str,
        communication_channel: str,
    ) -> str:
        
        
        """Generate a personalized document request message."""
        if not self.client:
            return self._generate_fallback_request(
                candidate_name, request_type, communication_channel
            )
        
        try:
            model = config('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo')
            
            system_prompt = """You are a professional HR assistant. Generate a polite, 
personalized email or message requesting identity documents (PAN and/or Aadhaar) 
from a candidate. The message should be:
- Professional and courteous
- Clear about what documents are needed
- Reassuring about data security
- Personalized with the candidate's name
Keep it concise (2-3 paragraphs)."""
            
            user_prompt = f"""Generate a document request message for:
Candidate Name: {candidate_name}
Email: {candidate_email}
Phone: {candidate_phone}
Documents Needed: {request_type}
Communication Channel: {communication_channel}

Generate the message now:"""
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return self._generate_fallback_request(
                candidate_name, request_type, communication_channel
            )
    
    def _generate_fallback_request(
        self,
        candidate_name: str,
        request_type: str,
        communication_channel: str,
        ) -> str:
        """Generate a basic request message without AI."""
        doc_types = {
            'pan': 'PAN card',
            'aadhaar': 'Aadhaar card',
            'both': 'PAN card and Aadhaar card',
        }
        
        doc_text = doc_types.get(request_type, 'PAN card and Aadhaar card')
        channel_text = 'email' if communication_channel == 'email' else 'phone'
        
        return f"""Dear {candidate_name or 'Candidate'},

We hope this message finds you well. As part of our onboarding process, we kindly request you to provide your {doc_text} for verification purposes.

Please upload the documents through our portal or send them via {channel_text}. All documents will be handled with strict confidentiality and in accordance with data protection regulations.

Thank you for your cooperation.

Best regards,
HR Team"""

