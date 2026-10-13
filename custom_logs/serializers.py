from rest_framework import serializers
from .models import KPIMaster, CustomWorkLog


class KPIMasterSerializer(serializers.ModelSerializer):
    perspective_display = serializers.CharField(source='get_perspective_display', read_only=True)

    class Meta:
        model = KPIMaster
        fields = [
            'id',
            'code',
            'perspective',
            'perspective_display',
            'name',
            'weight',
            'smart_target',
        ]


class CustomWorkLogSerializer(serializers.ModelSerializer):
    primary_kpi_details = KPIMasterSerializer(source='primary_kpi', read_only=True)
    additional_kpis_details = KPIMasterSerializer(source='additional_kpis', many=True, read_only=True)

    class Meta:
        model = CustomWorkLog
        fields = [
            'id',
            'title',
            'description',
            'date_performed',
            'hours_spent',
            'primary_kpi',
            'primary_kpi_details',
            'additional_kpis',
            'additional_kpis_details',
            'impact_result',
            'proof_type',
            'proof_reference',
            'proof_description',
            'created_at',
        ]
