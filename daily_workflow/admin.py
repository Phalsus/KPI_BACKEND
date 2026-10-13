from django.contrib import admin
from .models import DailyCheckin


@admin.register(DailyCheckin)
class DailyCheckinAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'scrum_attended',
        'scrum_joined_at',
        'jira_updated',
        'github_pushed',
        'has_potential_delay',
        'escalated_5_days_prior',
    )
    list_filter = (
        'scrum_attended',
        'jira_updated',
        'github_pushed',
        'has_potential_delay',
        'escalated_5_days_prior',
        'date',
    )
    search_fields = (
        'jira_tickets_worked',
        'daily_notes',
        'blockers',
        'delay_escalation_details',
    )
    date_hierarchy = 'date'
