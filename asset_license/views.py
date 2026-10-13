from rest_framework import viewsets, filters
from .models import (
    AssetBrand,
    AssetModel,
    AssetUser,
    HardwareAsset,
    SoftwareLicense,
)
from .serializers import (
    AssetBrandSerializer,
    AssetModelSerializer,
    AssetUserSerializer,
    HardwareAssetSerializer,
    SoftwareLicenseSerializer,
)
from common.permissions import (
    HardwareAssetPermission,
    SoftwareLicensePermission,
    AssetUserPermission,
    AssetBrandPermission,
    AssetModelPermission,
)


class HardwareAssetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for hardware inventory management with automatic Brand/Model/User
    provisioning and assignment history tracking.
    Protected by HardwareAssetPermission.
    """
    queryset = HardwareAsset.objects.select_related('brand', 'model', 'current_user').prefetch_related('assignment_history__user').all()
    serializer_class = HardwareAssetSerializer
    permission_classes = [HardwareAssetPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tag_id', 'serial_number', 'brand__name', 'model__name', 'current_user__full_name', 'status']
    ordering_fields = ['tag_id', 'created_at', 'last_info_updated_at', 'cost']
    ordering = ['-created_at']


class SoftwareLicenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tracking software subscriptions and renewal optimization.
    Protected by SoftwareLicensePermission.
    """
    queryset = SoftwareLicense.objects.all()
    serializer_class = SoftwareLicenseSerializer
    permission_classes = [SoftwareLicensePermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['software_name', 'vendor', 'optimization_plan']
    ordering_fields = ['renewal_date', 'annual_cost_usd']
    ordering = ['renewal_date']


class AssetUserViewSet(viewsets.ModelViewSet):
    queryset = AssetUser.objects.all()
    serializer_class = AssetUserSerializer
    permission_classes = [AssetUserPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'email', 'department']


class AssetBrandViewSet(viewsets.ModelViewSet):
    queryset = AssetBrand.objects.all()
    serializer_class = AssetBrandSerializer
    permission_classes = [AssetBrandPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class AssetModelViewSet(viewsets.ModelViewSet):
    queryset = AssetModel.objects.select_related('brand').all()
    serializer_class = AssetModelSerializer
    permission_classes = [AssetModelPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'brand__name']
