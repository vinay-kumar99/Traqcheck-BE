"""
Admin configuration for persistence models.
"""
from django.contrib import admin
from .models import CandidateModel, DocumentRequestModel, DocumentSubmissionModel


@admin.register(CandidateModel)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'designation', 'extraction_status', 'created_at']
    list_filter = ['extraction_status', 'created_at']
    search_fields = ['name', 'email', 'company']


@admin.register(DocumentRequestModel)
class DocumentRequestAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'request_type', 'status', 'created_at']
    list_filter = ['status', 'request_type', 'created_at']


@admin.register(DocumentSubmissionModel)
class DocumentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'document_type', 'verification_status', 'uploaded_at']
    list_filter = ['document_type', 'verification_status', 'uploaded_at']

