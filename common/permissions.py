from rest_framework import permissions


class BaseModelPermission(permissions.BasePermission):
    """
    Base permission class that inspects Django's permission framework
    (app_label.view_<model>, app_label.add_<model>, app_label.change_<model>, app_label.delete_<model>)
    or group memberships. Superusers retain universal access.
    """
    app_label = None
    model_name = None

    METHOD_ACTION_MAP = {
        'GET': 'view',
        'OPTIONS': 'view',
        'HEAD': 'view',
        'POST': 'add',
        'PUT': 'change',
        'PATCH': 'change',
        'DELETE': 'delete'
    }

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        # Resolve model permission codename
        action = self.METHOD_ACTION_MAP.get(request.method, 'view')
        perm = f"{self.app_label}.{action}_{self.model_name}"
        return request.user.has_perm(perm)


# ==============================================================================
# Model-Specific Authorization Classes
# ==============================================================================

# custom_logs permissions
class KPIMasterPermission(BaseModelPermission):
    app_label = 'custom_logs'
    model_name = 'kpimaster'


class CustomWorkLogPermission(BaseModelPermission):
    app_label = 'custom_logs'
    model_name = 'customworklog'

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.is_staff:
            return True
        # Read operations allowed if general model permission was met
        if request.method in permissions.SAFE_METHODS:
            return True
        # Modifications can be restricted to author if user field is present
        if hasattr(obj, 'created_by') and obj.created_by:
            return obj.created_by == request.user
        return True


# support_desk permissions
class SupportIncidentPermission(BaseModelPermission):
    app_label = 'support_desk'
    model_name = 'supportincident'


# daily_workflow permissions
class DailyCheckinPermission(BaseModelPermission):
    app_label = 'daily_workflow'
    model_name = 'dailycheckin'


# asset_license permissions
class HardwareAssetPermission(BaseModelPermission):
    app_label = 'asset_license'
    model_name = 'hardwareasset'


class SoftwareLicensePermission(BaseModelPermission):
    app_label = 'asset_license'
    model_name = 'softwarelicense'


class AssetUserPermission(BaseModelPermission):
    app_label = 'asset_license'
    model_name = 'assetuser'


class AssetBrandPermission(BaseModelPermission):
    app_label = 'asset_license'
    model_name = 'assetbrand'


class AssetModelPermission(BaseModelPermission):
    app_label = 'asset_license'
    model_name = 'assetmodel'


# inhouse_systems permissions
class InHouseSystemPermission(BaseModelPermission):
    app_label = 'inhouse_systems'
    model_name = 'inhousesystem'


# growth_conduct permissions
class LearningRecordPermission(BaseModelPermission):
    app_label = 'growth_conduct'
    model_name = 'learningrecord'


class BehavioralReviewRecordPermission(BaseModelPermission):
    app_label = 'growth_conduct'
    model_name = 'behavioralreviewrecord'


# kpi_summary (Scorecard) permission
class ScorecardSummaryPermission(permissions.BasePermission):
    """
    Grants access to executive summary based on 'kpi_summary.view_scorecard'
    or membership in 'Executive', 'Leadership', 'Executive / Leadership', or 'Manager' groups.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.is_staff:
            return True
        return (
            request.user.has_perm('kpi_summary.view_scorecard') or
            request.user.groups.filter(name__in=['Executive', 'Leadership', 'Manager', 'Executive / Leadership']).exists()
        )
