from rest_framework import viewsets, filters
from .models import LearningRecord, BehavioralReviewRecord
from .serializers import LearningRecordSerializer, BehavioralReviewRecordSerializer
from common.permissions import LearningRecordPermission, BehavioralReviewRecordPermission


class LearningRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for logging courses, certifications, and tracking <24h HR submission.
    Protected by LearningRecordPermission.
    """
    queryset = LearningRecord.objects.all()
    serializer_class = LearningRecordSerializer
    permission_classes = [LearningRecordPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'proof_reference']
    ordering_fields = ['completed_date', 'submitted_to_hr_date', 'score_pct']
    ordering = ['-completed_date']


class BehavioralReviewRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for 360 bi-annual behavioral review metrics and attendance adherence.
    Protected by BehavioralReviewRecordPermission.
    """
    queryset = BehavioralReviewRecord.objects.all()
    serializer_class = BehavioralReviewRecordSerializer
    permission_classes = [BehavioralReviewRecordPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['review_period', 'supervisor_feedback', 'proof_reference']
    ordering_fields = ['peer_review_score', 'attendance_adherence_pct', 'created_at']
    ordering = ['-created_at']
