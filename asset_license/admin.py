from django.contrib import admin
from .models import (
    AssetBrand,
    AssetModel,
    AssetUser,
    HardwareAsset,
    AssetAssignmentHistory,
    SoftwareLicense,
)


class AssetAssignmentHistoryInline(admin.TabularInline):
    model = AssetAssignmentHistory
    extra = 0
    readonly_fields = ('assigned_date', 'returned_date', 'notes')


@admin.register(HardwareAsset)
class HardwareAssetAdmin(admin.ModelAdmin):
    list_display = (
        'tag_id',
        'serial_number',
        'brand',
        'model',
        'asset_type',
        'current_user',
        'status',
        'last_info_updated_at',
    )
    list_filter = ('status', 'asset_type', 'brand', 'created_at')
    search_fields = ('tag_id', 'serial_number', 'current_user__full_name', 'status_details')
    inlines = [AssetAssignmentHistoryInline]


@admin.register(SoftwareLicense)
class SoftwareLicenseAdmin(admin.ModelAdmin):
    list_display = ('software_name', 'vendor', 'annual_cost_usd', 'renewal_date', 'is_active')
    list_filter = ('is_active', 'renewal_date')
    search_fields = ('software_name', 'vendor', 'optimization_plan')


@admin.register(AssetUser)
class AssetUserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'department')
    search_fields = ('full_name', 'email', 'department')


@admin.register(AssetBrand)
class AssetBrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(AssetModel)
class AssetModelAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name')
    list_filter = ('brand',)
    search_fields = ('name', 'brand__name')


@admin.register(AssetAssignmentHistory)
class AssetAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('asset', 'user', 'assigned_date', 'returned_date', 'notes')
    list_filter = ('assigned_date', 'returned_date')
    search_fields = ('asset__tag_id', 'user__full_name', 'notes')
