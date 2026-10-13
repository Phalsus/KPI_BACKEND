from rest_framework import serializers
from .models import SupportIncident


class SupportIncidentSerializer(serializers.ModelSerializer):
    ack_within_30m = serializers.BooleanField(read_only=True)
    solution_within_1h = serializers.BooleanField(read_only=True)
    resolved_within_4h = serializers.BooleanField(read_only=True)
    is_rtc_compliant = serializers.BooleanField(read_only=True)

    class Meta:
        model = SupportIncident
        fields = [
            'id',
            'ticket_ref',
            'title',
            'system_name',
            'reported_at',
            'acknowledged_at',
            'solution_provided_at',
            'resolved_at',
            'first_time_fix',
            'csat_score',
            'rca_notes',
            'ack_within_30m',
            'solution_within_1h',
            'resolved_within_4h',
            'is_rtc_compliant',
            'proof_type',
            'proof_reference',
            'proof_description',
            'created_at',
        ]
