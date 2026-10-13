from django.db import models
from common.models import ProofModel


class LearningRecord(ProofModel):
    """
    Tracks professional certifications and assigned training courses.
    Calculates HR submission compliance within 24 hours of completion.
    """
    class RecordType(models.TextChoices):
        CERTIFICATION = 'CERTIFICATION', 'Professional Certification'
        ASSIGNED_COURSE = 'ASSIGNED_COURSE', 'Company Assigned Training'

    title = models.CharField(max_length=255)
    record_type = models.CharField(max_length=30, choices=RecordType.choices)
    score_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Target >= 70.00% pass mark for assigned courses"
    )
    completed_date = models.DateField()
    submitted_to_hr_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_date', '-created_at']

    @property
    def submitted_within_24h(self) -> bool:
        if not self.submitted_to_hr_date or not self.completed_date:
            return False
        return (self.submitted_to_hr_date - self.completed_date).days <= 1

    def __str__(self):
        return f"[{self.get_record_type_display()}] {self.title} ({self.score_pct or 'N/A'}%)"


class BehavioralReviewRecord(ProofModel):
    """
    Tracks 360 bi-annual behavioral review metrics, peer review scores (target >= 4.0),
    zero escalation maintenance, and attendance adherence.
    """
    review_period = models.CharField(max_length=50)  # e.g., 'H1 2026'
    peer_review_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        help_text="Target >= 4.0 out of 5.0"
    )
    zero_escalations_maintained = models.BooleanField(default=True)
    attendance_adherence_pct = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    supervisor_feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.review_period} (Score: {self.peer_review_score}/5.0)"
