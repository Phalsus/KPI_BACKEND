from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class DailyCheckin(models.Model):
    """
    Tracks morning standup attendance (9:00 AM target), daily Jira/GitHub
    deliverables, blockers, and the 5-business-day advance delay escalation rule.
    """
    date = models.DateField(default=timezone.localdate, unique=True)
    scrum_attended = models.BooleanField(default=True)
    scrum_joined_at = models.TimeField(default='09:00:00')
    jira_updated = models.BooleanField(default=True)
    jira_tickets_worked = models.TextField(help_text="Comma-separated Jira IDs")
    github_pushed = models.BooleanField(default=True)
    github_pr_urls = models.TextField(blank=True, null=True)
    daily_notes = models.TextField()
    blockers = models.TextField(blank=True, null=True)

    # 5-day advance notice rule
    has_potential_delay = models.BooleanField(default=False)
    escalated_5_days_prior = models.BooleanField(
        default=False,
        help_text="Flagged at least 5 business days before deadline"
    )
    delay_escalation_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def clean(self):
        super().clean()
        if self.has_potential_delay and not self.delay_escalation_details:
            raise ValidationError({
                'delay_escalation_details': 'Details are required when flagging a potential delay.'
            })

    def __str__(self):
        return f"Daily Checkin [{self.date}] (Scrum: {'Attended' if self.scrum_attended else 'Missed'})"
