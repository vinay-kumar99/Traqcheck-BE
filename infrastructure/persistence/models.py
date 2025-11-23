from django.db import models
from django.core.validators import FileExtensionValidator


class CandidateModel(models.Model):
    
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=255, blank=True)
    designation = models.CharField(max_length=255, blank=True)
    skills = models.JSONField(default=list, blank=True)
    
    # Resume file
    resume_file = models.FileField(
        upload_to='resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
    )
    
    # Extraction metadata
    extraction_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending',
    )
    extraction_confidence = models.FloatField(default=0.0, null=True, blank=True)
    raw_extracted_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'candidates'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.name or 'Unknown'} - {self.email or 'No email'}"


class DocumentRequestModel(models.Model):
    
    candidate = models.ForeignKey(
        CandidateModel,
        on_delete=models.CASCADE,
        related_name='document_requests',
    )
    request_type = models.CharField(
        max_length=20,
        choices=[
            ('pan', 'PAN Card'),
            ('aadhaar', 'Aadhaar Card'),
            ('both', 'Both'),
        ],
        default='both',
    )
    request_message = models.TextField()
    communication_channel = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('both', 'Both'),
        ],
        default='email',
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('completed', 'Completed'),
        ],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'document_requests'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Document request for {self.candidate.name} - {self.status}"


class DocumentSubmissionModel(models.Model):
    
    candidate = models.ForeignKey(
        CandidateModel,
        on_delete=models.CASCADE,
        related_name='document_submissions',
    )
    document_type = models.CharField(
        max_length=20,
        choices=[
            ('pan', 'PAN Card'),
            ('aadhaar', 'Aadhaar Card'),
        ],
    )
    document_file = models.ImageField(
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])],
    )
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_submissions'
        ordering = ['-uploaded_at']
    
    def __str__(self) -> str:
        return f"{self.document_type} for {self.candidate.name}"

