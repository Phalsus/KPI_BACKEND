from django.contrib import admin
from .models import KPIMaster, CustomWorkLog


@admin.register(KPIMaster)
class KPIMasterAdmin(admin.ModelAdmin):
    list_display = ('code', 'perspective', 'name', 'weight')
    list_filter = ('perspective',)
    search_fields = ('code', 'name', 'smart_target')
    ordering = ('perspective', 'name')


@admin.register(CustomWorkLog)
class CustomWorkLogAdmin(admin.ModelAdmin):
    list_display = ('title', 'primary_kpi', 'date_performed', 'hours_spent', 'proof_type', 'created_at')
    list_filter = ('primary_kpi__perspective', 'proof_type', 'date_performed')
    search_fields = ('title', 'description', 'impact_result', 'proof_reference')
    date_hierarchy = 'date_performed'
    filter_horizontal = ('additional_kpis',)
