from django.contrib import admin
from .models import SupportIncident


@admin.register(SupportIncident)
class SupportIncidentAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_ref',
        'title',
        'system_name',
        'reported_at',
        'first_time_fix',
        'csat_score',
        'get_rtc_status',
    )
    list_filter = (
        'first_time_fix',
        'system_name',
        'proof_type',
        'reported_at',
    )
    search_fields = (
        'ticket_ref',
        'title',
        'system_name',
        'rca_notes',
        'proof_reference',
    )
    date_hierarchy = 'reported_at'

    @admin.display(boolean=True, description='RTC Compliant')
    def get_rtc_status(self, obj):
        return obj.is_rtc_compliant
