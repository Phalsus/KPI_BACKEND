from rest_framework import viewsets, filters
from .models import InHouseSystem
from .serializers import InHouseSystemSerializer
from common.permissions import InHouseSystemPermission


class InHouseSystemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing in-house software systems, tracking annual cost savings,
    efficiency metrics, and external commercial viability.
    Protected by InHouseSystemPermission.
    """
    queryset = InHouseSystem.objects.all()
    serializer_class = InHouseSystemSerializer
    permission_classes = [InHouseSystemPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['system_name', 'replaced_vendor_tool', 'proof_reference']
    ordering_fields = ['annual_cost_saved_usd', 'efficiency_pct', 'deployment_date', 'created_at']
    ordering = ['-annual_cost_saved_usd']
