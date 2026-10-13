from rest_framework import viewsets, filters
from .models import KPIMaster, CustomWorkLog
from .serializers import KPIMasterSerializer, CustomWorkLogSerializer
from common.permissions import KPIMasterPermission, CustomWorkLogPermission


class KPIMasterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing and viewing pre-defined KPI Master metrics.
    Protected by KPIMasterPermission (tied to custom_logs.view_kpimaster, etc.).
    """
    queryset = KPIMaster.objects.all()
    serializer_class = KPIMasterSerializer
    permission_classes = [KPIMasterPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name', 'perspective', 'smart_target']
    ordering_fields = ['perspective', 'name', 'weight']
    ordering = ['perspective', 'name']


class CustomWorkLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint for logging operational deliverables linked to specific KPIs.
    Protected by CustomWorkLogPermission (tied to custom_logs.view_customworklog, etc.).
    """
    queryset = CustomWorkLog.objects.select_related('primary_kpi').prefetch_related('additional_kpis').all()
    serializer_class = CustomWorkLogSerializer
    permission_classes = [CustomWorkLogPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'impact_result', 'proof_reference']
    ordering_fields = ['date_performed', 'created_at', 'hours_spent']
    ordering = ['-date_performed', '-created_at']
