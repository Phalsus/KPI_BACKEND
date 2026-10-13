from django.db import models
from common.models import ProofModel


class SupportIncident(ProofModel):
    """
    Tracks support incidents, Resolution-Time Compliance (RTC) SLAs,
    CSAT scores, and root-cause analysis (RCA).
    """
    ticket_ref = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    system_name = models.CharField(max_length=120)
    reported_at = models.DateTimeField()
    acknowledged_at = models.DateTimeField()
    solution_provided_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    first_time_fix = models.BooleanField(default=True)
    csat_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Target >= 90.00%"
    )
    rca_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reported_at', '-created_at']

    @property
    def ack_within_30m(self) -> bool:
        if not self.acknowledged_at or not self.reported_at:
            return False
        return (self.acknowledged_at - self.reported_at).total_seconds() <= 1800

    @property
    def solution_within_1h(self) -> bool:
        if not self.solution_provided_at or not self.reported_at:
            return False
        return (self.solution_provided_at - self.reported_at).total_seconds() <= 3600

    @property
    def resolved_within_4h(self) -> bool:
        if not self.resolved_at or not self.reported_at:
            return False
        return (self.resolved_at - self.reported_at).total_seconds() <= 14400

    @property
    def is_rtc_compliant(self) -> bool:
        return self.ack_within_30m and self.solution_within_1h and self.resolved_within_4h

    def __str__(self):
        return f"[{self.ticket_ref}] {self.title}"
