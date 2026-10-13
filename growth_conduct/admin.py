from django.contrib import admin
from .models import LearningRecord, BehavioralReviewRecord


@admin.register(LearningRecord)
class LearningRecordAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'record_type',
        'score_pct',
        'completed_date',
        'submitted_to_hr_date',
        'get_submitted_24h_status',
    )
    list_filter = ('record_type', 'completed_date', 'submitted_to_hr_date')
    search_fields = ('title', 'proof_reference')

    @admin.display(boolean=True, description='Submitted <24h')
    def get_submitted_24h_status(self, obj):
        return obj.submitted_within_24h


@admin.register(BehavioralReviewRecord)
class BehavioralReviewRecordAdmin(admin.ModelAdmin):
    list_display = (
        'review_period',
        'peer_review_score',
        'zero_escalations_maintained',
        'attendance_adherence_pct',
        'created_at',
    )
    list_filter = ('zero_escalations_maintained', 'created_at')
    search_fields = ('review_period', 'supervisor_feedback', 'proof_reference')
