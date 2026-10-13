from rest_framework import viewsets, filters
from .models import DailyCheckin
from .serializers import DailyCheckinSerializer
from common.permissions import DailyCheckinPermission


class DailyCheckinViewSet(viewsets.ModelViewSet):
    """
    API endpoint for logging and reviewing daily check-ins, scrum participation,
    and 5-day advance delay escalations.
    Protected by DailyCheckinPermission (tied to daily_workflow.view_dailycheckin, etc.).
    """
    queryset = DailyCheckin.objects.all()
    serializer_class = DailyCheckinSerializer
    permission_classes = [DailyCheckinPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['jira_tickets_worked', 'daily_notes', 'blockers', 'delay_escalation_details']
    ordering_fields = ['date', 'created_at', 'scrum_joined_at']
    ordering = ['-date']
