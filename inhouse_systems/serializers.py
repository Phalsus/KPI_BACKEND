from rest_framework import serializers
from .models import InHouseSystem


class InHouseSystemSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = InHouseSystem
        fields = [
            'id',
            'system_name',
            'replaced_vendor_tool',
            'annual_cost_saved_usd',
            'deployment_date',
            'status',
            'status_display',
            'efficiency_pct',
            'packageable_for_external_sale',
            'proof_type',
            'proof_reference',
            'proof_description',
            'created_at',
        ]
