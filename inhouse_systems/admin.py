from django.contrib import admin
from .models import InHouseSystem


@admin.register(InHouseSystem)
class InHouseSystemAdmin(admin.ModelAdmin):
    list_display = (
        'system_name',
        'replaced_vendor_tool',
        'annual_cost_saved_usd',
        'status',
        'efficiency_pct',
        'packageable_for_external_sale',
        'deployment_date',
    )
    list_filter = (
        'status',
        'packageable_for_external_sale',
        'deployment_date',
    )
    search_fields = (
        'system_name',
        'replaced_vendor_tool',
        'proof_reference',
    )
    date_hierarchy = 'deployment_date'
