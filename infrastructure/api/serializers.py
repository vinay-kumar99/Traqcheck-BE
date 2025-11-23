from rest_framework import serializers


class CandidateListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    company = serializers.CharField()
    designation = serializers.CharField()
    extraction_status = serializers.CharField()
    created_at = serializers.DateTimeField()


class DocumentSubmissionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    document_type = serializers.CharField()
    document_file_url = serializers.URLField(required=False, allow_null=True)
    verification_status = serializers.CharField()
    uploaded_at = serializers.DateTimeField(required=False, allow_null=True)


class DocumentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    request_type = serializers.CharField()
    request_message = serializers.CharField()
    communication_channel = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField(required=False, allow_null=True)


class CandidateDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    company = serializers.CharField()
    designation = serializers.CharField()
    skills = serializers.ListField(child=serializers.CharField())
    resume_file_url = serializers.URLField(required=False, allow_null=True)
    extraction_status = serializers.CharField()
    extraction_confidence = serializers.FloatField(required=False, allow_null=True)
    raw_extracted_data = serializers.DictField()
    document_requests = DocumentRequestSerializer(many=True)
    document_submissions = DocumentSubmissionSerializer(many=True)
    created_at = serializers.DateTimeField(required=False, allow_null=True)
    updated_at = serializers.DateTimeField(required=False, allow_null=True)


class CandidateUploadSerializer(serializers.Serializer):
    resume_file = serializers.FileField()
    
    def validate_resume_file(self, value):
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        return value


class RequestDocumentsSerializer(serializers.Serializer):
    request_type = serializers.CharField(default='both')
    communication_channel = serializers.CharField(default='email')


class SubmitDocumentSerializer(serializers.Serializer):
    document_type = serializers.CharField()
    document_file = serializers.FileField()

