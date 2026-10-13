from rest_framework import viewsets, filters
from .models import SupportIncident
from .serializers import SupportIncidentSerializer
from common.permissions import SupportIncidentPermission


class SupportIncidentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing support incidents and monitoring SLA RTC compliance.
    Protected by SupportIncidentPermission (tied to support_desk.view_supportincident, etc.).
    """
    queryset = SupportIncident.objects.all()
    serializer_class = SupportIncidentSerializer
    permission_classes = [SupportIncidentPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ticket_ref', 'title', 'system_name', 'rca_notes', 'proof_reference']
    ordering_fields = ['reported_at', 'acknowledged_at', 'resolved_at', 'csat_score']
    ordering = ['-reported_at']
