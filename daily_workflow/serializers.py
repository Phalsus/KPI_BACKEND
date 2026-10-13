from rest_framework import serializers
from .models import DailyCheckin


class DailyCheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyCheckin
        fields = [
            'id',
            'date',
            'scrum_attended',
            'scrum_joined_at',
            'jira_updated',
            'jira_tickets_worked',
            'github_pushed',
            'github_pr_urls',
            'daily_notes',
            'blockers',
            'has_potential_delay',
            'escalated_5_days_prior',
            'delay_escalation_details',
            'created_at',
        ]

    def validate(self, attrs):
        has_delay = attrs.get('has_potential_delay', getattr(self.instance, 'has_potential_delay', False))
        delay_details = attrs.get('delay_escalation_details', getattr(self.instance, 'delay_escalation_details', None))

        if has_delay and (not delay_details or not delay_details.strip()):
            raise serializers.ValidationError({
                'delay_escalation_details': 'Delay escalation details must be provided when a potential delay is flagged.'
            })
        return attrs
