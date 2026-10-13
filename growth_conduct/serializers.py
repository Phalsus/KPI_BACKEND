from rest_framework import serializers
from .models import LearningRecord, BehavioralReviewRecord


class LearningRecordSerializer(serializers.ModelSerializer):
    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)
    submitted_within_24h = serializers.BooleanField(read_only=True)

    class Meta:
        model = LearningRecord
        fields = [
            'id',
            'title',
            'record_type',
            'record_type_display',
            'score_pct',
            'completed_date',
            'submitted_to_hr_date',
            'submitted_within_24h',
            'proof_type',
            'proof_reference',
            'proof_description',
            'created_at',
        ]


class BehavioralReviewRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehavioralReviewRecord
        fields = [
            'id',
            'review_period',
            'peer_review_score',
            'zero_escalations_maintained',
            'attendance_adherence_pct',
            'supervisor_feedback',
            'proof_type',
            'proof_reference',
            'proof_description',
            'created_at',
        ]
